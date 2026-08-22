const help={
  'Build & Transfer':'Validated project package plus ownership handoff.',
  'Build & Deploy':'Live deployment plus customer handoff.',
  'Managed':'Live deployment with ongoing maintenance and version tracking.'
};
const mode=document.querySelector('#mode');
const modeHelp=document.querySelector('#modeHelp');
mode.addEventListener('change',()=>{modeHelp.textContent=help[mode.value]});
document.querySelector('#preview').addEventListener('click',()=>alert('Preview is available after the Factory quality gate.'));
document.querySelector('#handoff').addEventListener('click',()=>alert('Handoff includes repository, hosting, version, verification and support information.'));
