const {execFileSync}=require('child_process');const fs=require('fs'),path=require('path');let bad=0;
for(const f of fs.readdirSync(__dirname).filter(f=>f.endsWith('.test.js'))){
  const out=execFileSync('node',[path.join(__dirname,f)],{encoding:'utf8'});
  const fails=out.split('\n').filter(l=>/^(FAIL|TEST CRASH|CRASH)/.test(l));
  console.log((fails.length?'✗ ':'✓ ')+f+' ('+(out.match(/^PASS/gm)||[]).length+' passed)');fails.forEach(l=>console.log('   '+l));bad+=fails.length}
process.exit(bad?1:0);
