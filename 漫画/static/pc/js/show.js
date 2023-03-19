showTrueImg = function () {
    arr = $('.pic-content');
    for (i = 0; i < arr.length; i++) {
        url = arr[i].getAttribute("url");
        var img = new Image();
        img.setAttribute("num", i);
        img.onload = function () {
            arr[this.getAttribute('num')].setAttribute('src', this.src);
        }
        img.onerror = function () {
            arr[this.getAttribute('num')].setAttribute('src', '/static/pic/error.jpg');
        }
        img.src = url;
    }

}

$(window).ready(function () {
    showTrueImg();

    $('.pic-content').bind('looked', function () {
        if ($(this).offset().top > $(window).scrollTop() && $(this).offset().top < $(window).scrollTop() + window.screen.availHeight * 0.5) {
            $('#page-show').text($(this).attr('num') + "/" + count)
        }
    })

    var p = 0, t = 0;
    $(window).scroll(function () {
        p = $(this).scrollTop();
        if (t < p) {
            //下滚


        } else {
            //上滚

        }
        setTimeout(function () { t = p; }, 0)

        $('.pic-content').trigger('looked');

    })
});

function turn(tag) {
    if (tag == 0) {
        if (now == 0) {
            alert("这是第一章哦！");
        }
        else {
            window.location.href = "/" + mhid + "/" + (now - 1);
        }
    }
    if (tag == 1) {
        if (now == members - 1) {
            alert("这已经是最后一章了！");
        }
        else {
            window.location.href = "/" + mhid + "/" + (now + 1);
        }

    }
}

