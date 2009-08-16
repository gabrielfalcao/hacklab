SearchBox = $.klass({
    initialize: function (options) {
        this.settings = $.extend({
            focusClass: 'focused',
            defaultSearchText: "Search repositories"
        }, options);

        this.setup();
    },
    setup: function (){
        this.element.val(this.settings.defaultSearchText);
    },
    setFocused: function() {
        this.element.addClass(this.settings.focusClass);
    },
    setUnfocused: function() {
        this.element.removeClass(this.settings.focusClass);
    },
    onmouseout: function() {
        if (this.element.val() == this.settings.defaultSearchText) {
            this.setUnfocused();
        }
    },
    onfocus: function () {
        this.setFocused();
    },
    onmouseover: function () {
        this.setFocused();
    },
    onclick: function () {
        if (this.element.val() == this.settings.defaultSearchText) {
            this.element.val("");
        }
    }
});

$.hacklab.executeOnStartUp(function () {
    $("index.searchbox").attach(SearchBox, {
        focusClass: 'focused',
        defaultSearchText: "Search repositories"
    });
});