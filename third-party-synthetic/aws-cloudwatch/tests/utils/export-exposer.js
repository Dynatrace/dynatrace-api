exports._originalExports = {...exports};

if (typeof beforeExporter === 'function') {
    beforeExporter(exports);
}
