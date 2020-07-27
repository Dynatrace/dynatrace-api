const pageLoadBlueprint = async function () {
    return 42;
};

exports.handler = jest.fn(async () => {
    return await pageLoadBlueprint();
});
