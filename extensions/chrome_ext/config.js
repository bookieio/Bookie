YUI.GlobalConfig = {
    combine: true,
    base: '${combo}/combo?y/',
    fetchCSS: false,
    comboBase: '${combo}/combo?',
    maxURLLength: 1500,
    root: 'y/',
    groups: {
        bookie: {
            combine: true,
            base: '${combo}/combo?b',
            comboBase: '${combo}/combo?',
            root: 'b/',
            fetchCSS: false,
            filter: 'raw',
            // comes from including bookie/meta.js
            modules: YUI_MODULES,
        }
    }
};
