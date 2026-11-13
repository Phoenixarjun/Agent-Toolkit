import { readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { validateModel } from '../src/core/model.js';

const path=process.argv[2];
if(!path){console.error('Usage: node scripts/validate-model.mjs <visualize.json>');process.exit(2);}
try{
  const absolute=resolve(path);
  if(statSync(absolute).size>8*1024*1024)throw new Error('Model exceeds the 8MB viewer input limit');
  const model=JSON.parse(readFileSync(absolute,'utf8'));
  validateModel(model);
  console.log(JSON.stringify({valid:true,schema_version:model.schema_version,components:model.components.length,relations:model.relations.length,journeys:model.journeys.length,scenarios:model.scenarios.length,findings:model.findings.length},null,2));
}catch(error){
  console.error(`Model invalid: ${error.message}`);
  process.exit(1);
}
