var version = 19;

function getTable(username, password, callback) {
	if (!username) {
		data = getData();
		username = data.username;
		password = data.password;
	}
	mui.ajax('/course', {
		data: {
			'username': username,
			'password': password
		},
		dataType: 'json', //服务器返回json格式数据
		type: 'get', //HTTP请求类型
		timeout: 10000,
		success: function(data) {
			if (data.status == 'success') {
				//账号密码正确，加载后续数据
				//处理js
				var json = {
					'username': username,
					'password': password,
					'data': data
				}
				setData(json);
				return callback('数据请求成功！');
			} else if (data.status == 'fail') {
				//账号密码错误处理
				return callback("账号或密码错误");
			} else if (data.status == 'error') {
				return callback("\n程序正常连接到了服务器，\n但服务器无法连接到教务系统！\n稍后重试大概率解决问题（大概30S）。\n如一直失败则是学校VPN的问题。");
			} else {
				return callback("出现未知错误");
			}

		},
		error: function(xhr, type, errorThrown) {
			//异常处理；
			console.log(errorThrown)
			return callback("连接服务器失败！");

		},

	});

}

function upload(title, content, contact, callback) {

	contact = contact || "无";
	if (title == "" || content == "") {
		return callback("标题和内容都不能为空！");
	}
	if (title.length > 30) {
		return callback("标题要在30字以内！");
	}
	if (title.content > 200) {
		return callback("内容要在300字以内");
	}
	mui.ajax('/feedback', {
		dataType: 'json', //服务器返回json格式数据
		data: {
			'title': title,
			'content': content,
			'contact': contact
		},
		type: 'get', //HTTP请求类型
		timeout: 5000,
		success: function(data) {
			if (data.status == 'success') {
				return callback(data.info)
			}
		},
		error: function(xhr, type, errorThrown) {
			//异常处理；
			return callback("提交失败！")
		}
	});
}

function login(username, password, callback) {
	callback = callback || $.noop;
	username = username || '';
	password = password || '';
	setData();
	var num = isNaN(username);
	if (!isNaN(username) && username && password) {
		//正常登录流程
		return getTable(username, password, callback);
	} else {
		//返回错误
		return callback("\n1.账号密码不能为空\n2.学号必须为数字");
	};


}

function output(id, html) {
	$(id).html(html);
}

function calcTime(week) {

	data = getData();
	now = new Date();
	var root = new Date(data.data.root);
	root.setTime(root.getTime() + +60 * 60 * 1000 * 24 * 7 * (week - 1));
	month = root.getMonth() + 1; //月
	nowweek = getWeek(); //当前是第几周
	var head = [
		"<th class='month num' style='height: 10px;'>$month月</th>",
		"<th class='day choosen'>周一</br><font size='1' color='' class='date'>$day日</font></th>",
		"<th class='day choosen'>周二</br> <font size='1' color='' class='date'>$day日</font></th>",
		"<th class='day choosen'>周三</br> <font size='1' color='' class='date'>$day日</font></th>",
		"<th class='day choosen'>周四</br><font size='1' color='' class='date'>$day日</font></th>",
		"<th class='day choosen'>周五</br><font size='1' color='' class='date' class='date' class='date'>$day日</font></th>",
		"<th class='day choosen'>周六</br><font size='1' color='' class='date' class='date'>$day日</font></th>",
		"<th class='day choosen'>周日</br> <font size='1' color='' class='date'>$day日</font></th>"
	]; 
	head[0] = head[0].replace('$month', month);
	string = ''
	for (i = 1; i < head.length; i++) {

		head[i] = head[i].replace("$day", root.getDate());
		if (root.getFullYear() == now.getFullYear() && root.getMonth() == now.getMonth() && root.getDate() == now.getDate()) {
			//console.log('1');
		} else {
			head[i] = head[i].replace(" choosen", '');
		}
		string += head[i];
		root.setTime(root.getTime() + 60 * 60 * 1000 * 24);
	}
	string = '<tr>' + head[0] + string + '</tr>';
	output("#days", string)

}

function getWeek() {
	data = getData();
	var rootTime = data.data.root;
	var rootTime = "2020/09/07"
	var date = new Date()
	var now = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
	var endTime = new Date(rootTime).getTime() / 1000 - parseInt(new Date().getTime() / 1000);
	var timeDay = parseInt(endTime / 60 / 60 / 24) * -1; //相差天数
	if (timeDay < 0) timeDay = 0;
	var week = Math.floor(timeDay / 7) + 1;
	return week;
}

function fresh(week) {
	thisweek = getWeek();
	if (!week) week = thisweek;
	$('#table').html(data.data.course[week]);
	if(week == thisweek){
		$('#num').text("第" + week + "周" + '');
	}
	else{
		$('#num').html("<span style='color: red;'>" + "第" + week + "周"+"</span>");
	}
	
	mui('.mui-numbox').numbox().setValue(week);
	calcTime(week);
}

getData = function() {
	var stateText = localStorage.getItem('$data') || "{}";
	return JSON.parse(stateText);
};

setData = function(state) {
	state = state || {};
	localStorage.setItem('$data', JSON.stringify(state));
};

//检查更新
function checkUpdate() {
	
	mui.ajax('/update', {
		dataType: 'json', //服务器返回json格式数据
		data: {
			'version': version
		},
		type: 'get', //HTTP请求类型
		timeout: 5000,
		success: function(data) {
			if (data.status != 'yes') {
				var btnArray = ['取消', '自动更新'];
				mui.confirm(data.info, '检测到版本更新', btnArray, function(e) {
					if (e.index == 1) {
						//setData();
						downWgt();

					}
				})

			}
		},
		error: function(xhr, type, errorThrown) {
			//异常处理；
			mui.toast("检查更新失败！");
		}
	});
}


// 自动更新
function downWgt() {
	var wgtUrl = "/download";
	plus.nativeUI.showWaiting("下载更新文件中...");
	plus.downloader.createDownload(wgtUrl, {
		filename: "_doc/update/"
	}, function(d, status) {
		if (status == 200) {
			//console.log("下载wgt成功：" + d.filename);
			installWgt(d.filename); // 安装wgt包  
		} else {
			//console.log("下载wgt失败！");
			mui.toast("下载更新文件失败！")
		}
		plus.nativeUI.closeWaiting();
	}).start();
}

function installWgt(path) {
	plus.nativeUI.showWaiting("安装wgt文件...");
	plus.runtime.install(path, {}, function() {
		plus.nativeUI.closeWaiting();
		console.log("安装wgt文件成功！");
		mui.toast("自动更新安装完成！请重新打开应用");
		// setTimeout(function(){
		// 	plus.runtime.restart();
		// },3000); 
		//plus.runtime.restart();
	}, function(e) {
		plus.nativeUI.closeWaiting();
		mui.toast("安装更新文件失败：" + e.message);
	});
}
