$.extend({
    hacklab: {
        startupActions: [],
        debug: function (what) {
            if (console)
                console.debug(what);
        },
        go: function () {
            for (var i in this.startupActions) {
                this.startupActions[i]();
            }
        },
        executeOnStartUp: function (callable){
            next = this.startupActions.length;
            this.startupActions[next] = callable;
        }
    }
});
