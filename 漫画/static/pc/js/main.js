$(window).ready(function() {
	$('.type-name').hover(function() {
		text = $(this).attr('attr')
		arr = $('.full');
		for (i = 0; i < arr.length; i++) {

			if ($(arr[i]).attr('class').indexOf(text) >= 0) {
				$(arr[i]).css('display', 'flex');
			} else {
				$(arr[i]).css('display', 'none');
			}
		}
	}, null);

	$('#head').hover(function() {
		$('#title').css('height','100vh');
	}, function(){
		$('#title').css('height','150px');
	});

	$('#logo').on('click',function(){
		window.location.href = '/';
	})

	$('#head_bottom').html(path);

});

function change(){
	if($("#shoter").text() == '展开'){
		$('#chapter-content').css('max-height','');
		$("#shoter").text('收起');
	}
	else{
		$('#chapter-content').css('max-height','200px');
		$("#shoter").text('展开');
	}
}

function search(){
	content = $('#search_content').val();
	if(content != '') window.location.href = '/search?name=' + content;
}