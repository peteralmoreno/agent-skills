#!/usr/bin/env node
/**
 * Lightweight mechanical validator for LENS v1 Markdown plans.
 * It checks shape and some reference integrity, not engineering quality or user approval.
 *
 * node lens/scripts/validate-plan.mjs plans/foo-lens.md [--prism specs/foo-prism.md] [--json]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HEADINGS = [
  '## L — Limits',
  '## E — Execution plan',
  '## N — Needs',
  '## S — Signals',
  '## Handoff',
];
const DELIVERY = new Set(['Now', 'Later', 'Outside this delivery']);
const STATUS = new Set(['draft', 'blocked', 'approved']);
const SOURCE_STATUS = new Set(['draft', 'approved', 'unknown']);

function allIds(text, letter) {
  const pattern = new RegExp(`\\b${letter}\\d+\\b`, 'g');
  return [...new Set(text.match(pattern) ?? [])];
}

function parseFrontMatter(text) {
  const m = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(text);
  if (!m) return null;
  const fields = {};
  for (const line of m[1].split(/\r?\n/)) {
    if (/^\s*(#|$)/.test(line)) continue;
    const kv = /^([a-z][a-z_]*):\s*(.*)\s*$/.exec(line);
    if (!kv) continue;
    let value = kv[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) value = value.slice(1, -1);
    fields[kv[1]] = value;
  }
  return fields;
}

function parseMarkdownTable(text, expectedColumns, label, errors) {
  const lines = text.split(/\r?\n/).map(x => x.trim());
  const headerIndex = lines.findIndex(line => line.startsWith('|'));
  if (headerIndex < 0) {
    errors.push(`${label}: missing Markdown table`);
    return [];
  }
  const cellize = line => line.replace(/^\|\s*|\s*\|$/g, '').split('|').map(x => x.trim());
  const columns = cellize(lines[headerIndex]);
  if (columns.length !== expectedColumns.length || expectedColumns.some((x,i) => columns[i] !== x)) {
    errors.push(`${label}: expected columns: ${expectedColumns.join(' | ')}`);
    return [];
  }
  if (!/^\|?\s*:?-{3,}/.test(lines[headerIndex + 1] ?? '')) {
    errors.push(`${label}: missing table separator row`);
    return [];
  }
  const rows = [];
  for (const line of lines.slice(headerIndex + 2)) {
    if (line === '' && rows.length > 0) break;
    if (!line.startsWith('|')) continue;
    const cells = cellize(line);
    if (cells.length !== columns.length) { errors.push(`${label}: row has ${cells.length} columns instead of ${columns.length}`); continue; }
    rows.push(cells);
  }
  if (rows.length === 0) errors.push(`${label}: expected at least one data row`);
  return rows;
}

function sliceSection(text, headings, index) {
  const from = text.indexOf(headings[index]);
  if (from < 0) return '';
  const next = index + 1 < headings.length ? text.indexOf(headings[index + 1], from + headings[index].length) : -1;
  return text.slice(from + headings[index].length, next < 0 ? text.length : next);
}
function subSection(text, name) {
  const match = new RegExp(`^### ${name}\\s*$`, 'm').exec(text);
  if (!match) return null;
  const start = match.index + match[0].length;
  const next = /^#{2,3} /gm;
  next.lastIndex = start;
  const candidate = next.exec(text);
  return text.slice(start, candidate ? candidate.index : text.length);
}

function specIds(text, letter) {
  // Require a declaration-like row or sentence start, not a casual mention in prose.
  // Examples: R1. ..., - I1: ..., | M1 | ...
  const expression = new RegExp(`^\\s*(?:[-*]\\s+|\\|\\s*)?(${letter}\\d+)(?=\\s*(?:[.):-]|—|\\|))`, 'gm');
  return new Set([...text.matchAll(expression)].map(m => m[1]));
}
function hasCycle(dependencies) {
  const state = new Map();
  function visit(n) {
    if (state.get(n) === 1) return true;
    if (state.get(n) === 2) return false;
    state.set(n, 1);
    for (const dep of dependencies.get(n) ?? []) if (dependencies.has(dep) && visit(dep)) return true;
    state.set(n, 2);
    return false;
  }
  return [...dependencies.keys()].some(visit);
}

export function validatePlan(markdown, options = {}) {
  const errors = [], warnings = [];
  const meta = parseFrontMatter(markdown);
  if (!meta) errors.push('Missing YAML front matter delimited by ---');
  const fields = meta ?? {};
  for (const required of ['format', 'status', 'source_spec', 'source_status', 'delivery_target']) {
    if (!fields[required] || fields[required].includes('<')) errors.push(`Missing or placeholder metadata: ${required}`);
  }
  if (fields.format && fields.format !== 'lens/v1') errors.push('format must equal lens/v1');
  if (fields.status && !STATUS.has(fields.status)) errors.push('status must be draft, blocked, or approved');
  if (fields.source_status && !SOURCE_STATUS.has(fields.source_status)) errors.push('source_status must be draft, approved, or unknown');
  if (fields.status === 'approved' && fields.source_status !== 'approved') errors.push('Approved LENS requires source_status: approved');
  const positions = HEADINGS.map(h => markdown.indexOf(h));
  for (let i = 0; i < HEADINGS.length; i++) {
    if (positions[i] < 0) errors.push(`Missing required heading: ${HEADINGS[i]}`);
    if (i && positions[i] >= 0 && positions[i - 1] >= 0 && positions[i] <= positions[i - 1]) errors.push(`Heading out of order: ${HEADINGS[i]}`);
    const count = (markdown.split(HEADINGS[i]).length - 1);
    if (count > 1) errors.push(`Repeated heading: ${HEADINGS[i]}`);
  }
  if (errors.some(e => e.startsWith('Missing required heading') || e.startsWith('Heading out of order'))) {
    return { ok: false, errors, warnings, metadata: fields };
  }

  const l = sliceSection(markdown, HEADINGS, 0);
  const e = sliceSection(markdown, HEADINGS, 1);
  const n = sliceSection(markdown, HEADINGS, 2);
  const s = sliceSection(markdown, HEADINGS, 3);
  const handoff = sliceSection(markdown, HEADINGS, 4);

  for (const subsection of ['Now', 'Later', 'Outside this delivery', 'Requirement coverage']) {
    if (!subSection(l, subsection)) errors.push(`Limits requires subsection: ### ${subsection}`);
  }
  const coverageText = subSection(l, 'Requirement coverage') || '';
  const coverage = parseMarkdownTable(coverageText, ['PRISM ID', 'Delivery', 'Reason / next step'], 'Requirement coverage', errors);
  const coverageByID = new Map();
  for (const [id, delivery, reason] of coverage) {
    if (!/^R\d+$/.test(id)) errors.push(`Invalid requirement ID: ${id}`);
    if (!DELIVERY.has(delivery)) errors.push(`${id}: delivery must be Now, Later or Outside this delivery`);
    if (!reason || /^<.*>$/.test(reason)) errors.push(`${id}: explain placement and next step`);
    if (coverageByID.has(id)) errors.push(`Duplicate requirement coverage: ${id}`);
    coverageByID.set(id, { delivery, reason });
  }
  const work = parseMarkdownTable(e, ['Work ID', 'Deliverable / action', 'Depends on', 'PRISM links', 'Done when'], 'Execution plan', errors);
  const workByID = new Map(), deps = new Map();
  for (const [id, action, dependsOn, links, done] of work) {
    if (!/^W\d+$/.test(id)) errors.push(`Invalid work ID: ${id}`);
    if (workByID.has(id)) errors.push(`Duplicate work unit: ${id}`);
    if (!action || action.startsWith('<') || !done || done.startsWith('<')) errors.push(`${id}: specify a concrete outcome and Done when`);
    if (allIds(links,'R').length + allIds(links,'I').length + allIds(links,'S').length === 0) errors.push(`${id}: missing PRISM R/I/S links`);
    const d = allIds(dependsOn, 'W');
    deps.set(id, d);
    workByID.set(id, { action, links, done });
  }
  for (const [id, depList] of deps) {
    for (const dep of depList) {
      if (dep === id) errors.push(`${id}: cannot depend on itself`);
      else if (!workByID.has(dep)) errors.push(`${id}: unknown dependency ${dep}`);
    }
  }
  if (hasCycle(deps)) errors.push('Execution plan contains cyclic dependencies');
  for (const [id, status] of coverageByID) {
    if (status.delivery === 'Now' && ![...workByID.values()].some(w => allIds(w.links,'R').includes(id))) errors.push(`${id}: Now requirement has no work-unit link`);
  }
  const needsText = n.trim();
  if (!/None — confirmed/.test(needsText)) {
    const needRows = parseMarkdownTable(needsText, ['Need ID', 'Type', 'Description', 'Resolve before'], 'Needs', errors);
    const needIds = new Set();
    for (const [id, type, description, when] of needRows) {
      if (!/^N\d+$/.test(id)) errors.push(`Invalid need ID: ${id}`);
      if (needIds.has(id)) errors.push(`Duplicate need ID: ${id}`);
      needIds.add(id);
      if (!['Blocker','Risk','Question'].includes(type)) errors.push(`${id}: invalid need type ${type}`);
      if (!description || description.startsWith('<') || !when || when.startsWith('<')) errors.push(`${id}: needs description and resolution checkpoint`);
      if (type === 'Blocker' && fields.status === 'approved') errors.push(`${id}: approved plan cannot contain unresolved Blocker`);
    }
  }
  const signalRows = parseMarkdownTable(s, ['Work ID', 'PRISM measures', 'Evidence to collect'], 'Signals', errors);
  const signalWorkIds = new Set();
  for (const [id, measures, evidence] of signalRows) {
    if (!workByID.has(id)) errors.push(`Signals references unknown work unit: ${id}`);
    if (signalWorkIds.has(id)) errors.push(`Duplicate Signals work unit: ${id}`);
    signalWorkIds.add(id);
    if (allIds(measures, 'M').length === 0) errors.push(`${id}: Signals must reference PRISM M#`);
    if (!evidence || evidence.startsWith('<')) errors.push(`${id}: describe evidence to collect`);
    if (/\bPASS(?:ED)?\b/i.test(evidence)) warnings.push(`${id}: a plan should specify future evidence, not claim PASS results`);
  }
  for (const id of workByID.keys()) if (!signalWorkIds.has(id)) errors.push(`${id}: no planned verification in Signals`);
  if (!/\*\*Readiness:\*\*/.test(handoff)) errors.push('Handoff missing Readiness');
  if (!/\*\*Next step:\*\*/.test(handoff)) errors.push('Handoff missing Next step');
  if (!/\*\*Authority:\*\*/.test(handoff)) errors.push('Handoff missing source authority statement');
  if (fields.status === 'approved' && !/Ready for (?:implementation )?handoff/i.test(handoff)) errors.push('Approved plan requires Ready for handoff in Handoff');

  if (typeof options.prismText === 'string') {
    const source = options.prismText;
    const ids = Object.fromEntries(['R','I','S','M'].map(letter => [letter,specIds(source,letter)]));
    if (ids.R.size === 0) warnings.push('Source PRISM has no recognizable R# declarations; source-ID validation may be incomplete');
    if (ids.M.size === 0) warnings.push('Source PRISM has no recognizable M# declarations; measure validation may be incomplete');
    if (ids.R.size > 0) {
      for (const id of ids.R) if (!coverageByID.has(id)) errors.push(`PRISM requirement ${id} is not classified in Limits`);
      for (const id of coverageByID.keys()) if (!ids.R.has(id)) errors.push(`Coverage references unknown PRISM requirement ${id}`);
    }
    for (const [id,w] of workByID) {
      for (const letter of ['R','I','S']) {
        if (ids[letter].size === 0) continue;
        for (const ref of allIds(w.links, letter)) if (!ids[letter].has(ref)) errors.push(`${id}: unknown PRISM ${ref}`);
      }
    }
    if (ids.M.size > 0) for (const [id,measures] of signalRows.map(row=>[row[0],row[1]])) {
      for (const ref of allIds(measures,'M')) if (!ids.M.has(ref)) errors.push(`${id}: unknown PRISM measure ${ref}`);
    }
  } else {
    warnings.push('PRISM source not supplied: cannot check R/I/S/M IDs against authoritative spec');
  }

  return { ok: errors.length === 0, errors, warnings, metadata: fields,
    counts: { requirements: coverageByID.size, work_units: workByID.size, signal_rows: signalRows.length } };
}

function printHelp() {
  console.log('Usage: node lens/scripts/validate-plan.mjs <plan.md> [--prism <source-prism.md>] [--json]');
  console.log('Checks LENS structure/links only; does not check engineering feasibility or user authorization.');
}

async function main(args) {
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) { printHelp(); return args.length === 0 ? 2 : 0; }
  const json = args.includes('--json');
  const prismPos = args.indexOf('--prism');
  if (prismPos >= 0 && !args[prismPos + 1]) { console.error('--prism requires a path'); return 2; }
  const planArg = args[0];
  if (planArg.startsWith('--')) { console.error('First argument must be a LENS document path'); return 2; }
  let content;
  try { content = fs.readFileSync(planArg, 'utf8'); }
  catch (err) { console.error(`Cannot read plan: ${err.message}`); return 2; }
  const metadata = parseFrontMatter(content) ?? {};
  let prismText;
  if (prismPos >= 0) {
    try { prismText = fs.readFileSync(args[prismPos + 1], 'utf8'); }
    catch (err) { console.error(`Cannot read PRISM source: ${err.message}`); return 2; }
  } else if (metadata.source_spec && !/^https?:\/\//i.test(metadata.source_spec)) {
    const choices = [path.resolve(metadata.source_spec), path.resolve(path.dirname(planArg), metadata.source_spec)];
    for (const candidate of choices) if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
      prismText = fs.readFileSync(candidate,'utf8'); break;
    }
  }
  const report = validatePlan(content, { prismText });
  if (json) console.log(JSON.stringify(report, null, 2));
  else {
    console.log(`LENS ${report.ok ? 'structural check passed' : 'structural check failed'}`);
    for (const err of report.errors) console.log(`ERROR: ${err}`);
    for (const warning of report.warnings) console.log(`WARN: ${warning}`);
    if (report.ok) console.log('This does not prove technical readiness or approval.');
  }
  return report.ok ? 0 : 1;
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const code = await main(process.argv.slice(2));
  process.exitCode = code;
}
