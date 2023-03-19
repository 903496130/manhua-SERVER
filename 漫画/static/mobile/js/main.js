showTrueImg = function(){
    arr = $('.mui-card')
    for(i = 0;i < arr.length;i++){
        url = arr[i].getAttribute("cover");
        var img = new Image();
        img.setAttribute("num",i);
        img.onload = function(){
            arr[this.getAttribute('num')].setAttribute('style','background-image: url(' + this.src + ')');
            arr[this.getAttribute('num')].classList.add("show");
        }
        img.onerror = function() {
            arr[this.getAttribute('num')].setAttribute('src','/source/pic/error.jpg');
        }
        img.src = url;
    }
}

showTrueImg2 = function(a){
    url = a.attr("cover");
    var img = new Image();
    img.onload = function(){
        $(a).attr('style','background-image: url(' + this.src + ')');
        $(a).addClass("show");
    }
    img.onerror = function() {
        $(a).attr('style','background-image: /source/pic/error.jpg');
    }
    img.src = url;

}

$(document).ready(function() {
    //页面上下滚动事件
    $(window).scroll(function() {
        p = $(this).scrollTop();
        height = $('#header').height();
        if (p < height) {
            $('.mui-title').css('visibility', 'hidden');
        } else {
            $('.mui-title').css('visibility', '');
        }
    })
    //showTrueImg();
    $("#num").scrollLeft($($('.page')[page-1]).offset().left - $('#num').width()*0.5);


})

function add() {
    mui.prompt('从\nhttp://99.hhxxee.com\n获取连接', '', '输入链接', ['取消', '确认'], function(e) {
        if (e.index == 1) {
            if (e.value != '') {
                mui.get('/add', {
                    'url': e.value
                }, function(data) {
                    //获得服务器响应
                    mui.toast(data, {
                        duration: 'long',
                        type: 'div'
                    })
                }, 'text');
            } else {
                mui.toast("请输入链接！", {
                        duration: 'long',
                        type: 'div'
                    })
            }

        }

    }, 'div')

}

//换页

function turn(tag){

    if(tag == 1){
        //上一页
        if (page <= 1){
            mui.toast('这是第一页！', {
                duration: 'short',
                type: 'div'
            });
        }
        else{
            window.location.href = last;
        }
    }
    else{
        //下一页
        if (page >= totalPage){
            mui.toast('这是最后一页！', {
                duration: 'short',
                type: 'div'
            });
        }
        else{
            window.location.href = next;
        }
    }
}

