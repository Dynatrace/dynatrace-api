declare namespace NodeJS {
    interface Global {
        beforeExporter?: (moduleExports: any) => void;
        _testName: string;
    }
}
