const concat = require('concat');
const fs = require('fs');

const outDir = './out';
const exportExposer = `./utils/export-exposer.js`;
const dynatraceCanaryExporter = '../dynatrace-canary-exporter.js';

export const buildAndLoadCanary = async (canaryPath?: string) => {
    const files = canaryPath
        ? [canaryPath, exportExposer, dynatraceCanaryExporter]
        : [exportExposer, dynatraceCanaryExporter];

    const { relativeToCurrDir, relativeToProjectRoot } = getOutPaths();

    if (!fs.existsSync(outDir)){
        fs.mkdirSync(outDir);
    }
    
    return concat(files, relativeToProjectRoot).then(() =>
        require(relativeToCurrDir));
};

const getOutPaths = () => {
    // Use a different file for each test to prevent loading cached modules and still allow debugging
    // _testName is set in jest.setup.js
    const fileName = global._testName.toLowerCase().replace(/[\s/,]/g, '-');
    const outPath = `${outDir}/${fileName}.test-canary.js`
    return {
        relativeToCurrDir: `../${outPath}`,
        relativeToProjectRoot: `./${outPath}`,
    };
};
