$(function () {
    let night_button = $(".night-button");

    night_button.on("click", function (e) {
        $("html").toggleClass('night-mode');
        localStorage.setItem("night-mode", localStorage.getItem("night-mode") === 'no' ? 'yes' : 'no');
    });

    if (localStorage.getItem("night-mode") == null) {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            localStorage.setItem("night-mode", 'yes');
        } else {
            localStorage.setItem("night-mode", 'no');
        }
    }

    if (localStorage.getItem("night-mode") === 'yes') {
        $("html").toggleClass('night-mode');
    }
});