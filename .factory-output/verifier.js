const fs = require('fs');
const path = require('path');

function verifyWorkflow() {
  console.log('--- RUNNING GOLDEN REFERENCE WORKFLOW VERIFICATION ---');
  
  const workflowPath = path.join(__dirname, 'workflow.json');
  if (!fs.existsSync(workflowPath)) {
    console.error('FAILED: workflow.json is missing.');
    process.exit(1);
  }

  const rawData = fs.readFileSync(workflowPath);
  const workflow = JSON.parse(rawData);

  let allPassed = true;
  workflow.pipeline.forEach((step, index) => {
    const verified = step.status === 'completed' && step.evidence.length > 0;
    if (verified) {
      console.log(`[PASS] ${step.stage} -> Evidence: ${step.evidence}`);
    } else {
      console.error(`[FAIL] ${step.stage} did not meet criteria.`);
      allPassed = false;
    }
  });

  if (allPassed) {
    console.log('\nAll stages verified successfully with real evidence.');
    process.exit(0);
  } else {
    process.exit(1);
  }
}

verifyWorkflow();
