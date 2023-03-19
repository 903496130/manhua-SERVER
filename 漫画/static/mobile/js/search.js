$(document).ready(function() {
    $("#keyword").on('tap',function(){
        //console.log("开始输入");
    });

    $("#keyword").on('blur',function(){
        //console.log("失去焦点，输入结束");
        setTimeout(() => {
            $("#tips").html(null);
            $('#tips').css('display',"none");
        }, 100);
    });

    $("#keyword").on('input',function(){
        value = this.value;
        if(value != ""){

            arr1 = value.split(" ");
            arr2 = [];

            mui.get('/tips',{'value':value},function(data){
                html = "";
                //关键字数组去重，arr2是去重后的结果
                for(i = 0;i < arr1.length;i++){
                    if(arr2.indexOf(arr1[i]) == -1 && arr1[i] != ""){
                        arr2.push(arr1[i]);
                    }
                }

                //关键字替换
                for(i = 0;i < data.result.length;i++){
                    for(m = 0;m < arr2.length;m++){
                        reg = RegExp(arr2[m],'ig');
                        data.result[i][0] = data.result[i][0].replace(reg,"<font color='red'>" + arr2[m] + "</font>");
                    }
                }

                if(data.result.length == 0){
                    $("#tips").html(null);
                    return;
                }

                for(i = 0;i < data.result.length;i++){
                    html += "<a href='/" + data.result[i][1] + "'><span class='tip'>" + data.result[i][0] + "</span></a>"
                }
                //关键字高亮处理
                if(html != ""){
                    html += "<span style='color:blue'>===共" + data.count + "条结果===</span>"
                    $('#tips').css('display',"block");
                    $("#tips").html(html);
                }

            },'json');
        }
        else{
            $('#tips').css('display',"none");
            $("#tips").html(null);
        }
    });

    $("#search").on('tap',function(){
        window.location.href = '/search?name=' + $("#keyword").val();
    });

    showTrueImg();
});

function setTipPosition() {
    height = $("#input").height();
    width = $("#input").width();
    left = $("#input").offset().left;
    top1 = $("#input").offset().top;
    $("#tips").css('display', 'block');
    $("#tips").css('width', width + 6 + 'px');
    $("#tips").css('left', left + 'px');
    $("#tips").css('top', top1 + height + 'px');
    console.log(height, width, left, top1);
}

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

function calAge(e) {
    var evt = window.event || e;
    if (evt.keyCode == 13) {
        $("#search").trigger('tap');
        $("#search1").trigger('tap');
    }
}
