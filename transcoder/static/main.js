function ajax (method,url,callback,data) {
    var request;
    try {
        request = new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
        try {
            request = new ActiveXObject("Microsoft.XMLHTTP");
        } catch (E) {
            request = false;
          }
      }
    if (!request && typeof XMLHttpRequest!='undefined') {
        request = new XMLHttpRequest();
    }
    if (!request)
        alert("Error initializing XMLHttpRequest!");   
     
    request.open(method,url,true);
    request.onreadystatechange = function () {
 
        if (request.readyState == 4){
            callback.call(request.responseText);
        }
    }
    if (method=='POST') {
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    }
    request.send(data);    

}

function fill (input) {
	
	var name=document.getElementsByClassName(input.name);
	if (name){
        for(i=0;i<name.length;i++){
		    name[i].innerHTML=input.value;
	    }
	}		

}

function showInfo (btn) {
	btn.setAttribute('onclick','closeInfo(this)');
	btn.innerHTML='<span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span>'
	var channelDiv=btn.parentNode.parentNode;
	var url='/show_channel/'+channelDiv.id;
    ajax ('GET',url,function(){channelDiv.innerHTML += this;});
}

function closeInfo (btn) {
	btn.setAttribute('onclick','showInfo(this)');
	btn.innerHTML='<span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>'
	btn.parentNode.parentNode.removeChild(btn.parentNode.parentNode.getElementsByClassName('log')[0]);
	btn.parentNode.parentNode.removeChild(btn.parentNode.parentNode.getElementsByClassName('ch_info')[0]);
}

function editChannel (span) {
	var name=span.getAttribute('name');
	var data=span.previousElementSibling.innerHTML;
    span.previousElementSibling.style.display='none';
    span.className='glyphicon glyphicon-ok edit';
    span.setAttribute('onclick','saveChannel(this)');

    if (name != 'command'){
        var input = document.createElement('input');
        span.parentNode.insertBefore(input,span);
        input.value=data;
        input.className='input_ch_data';    	
    }
    else {
        var textArea = document.createElement('textArea');
        span.parentNode.insertBefore(textArea,span);
        textArea.value=data;
        textArea.className='input_ch_data';	
        textArea.setAttribute('cols','120');
        textArea.setAttribute('rows','3');
    }
    
}

function saveChannel(span) {

	var name=span.getAttribute('name');
	var chID=find_channel_block (span);
    
    if (span.nextElementSibling.className=='error') {
       	span.parentNode.removeChild(span.nextElementSibling);
    }
    
    var newData=span.previousElementSibling.value.replace(/(^\s+|\s+$)/g,'');
    var oldData=span.previousElementSibling.previousElementSibling.innerHTML.replace(/(^\s+|\s+$)/g,'');

    if (newData == oldData){
    	saveDone ('done',span);
    	return;
    }

    var url = '/edit_channel_data/'+ chID.id + '/' + name +'/' + span.previousElementSibling.value;
    ajax ('GET',url,function(){ saveDone(this,span) });

}

function saveDone (message,sp) {
    
    var input=sp.previousElementSibling;  
    var dataSpan=input.previousElementSibling;

	if (message.replace(/\s+/g, '')=='done') {
		dataSpan.removeAttribute('style');
		dataSpan.innerHTML=input.value;
        
        if (sp.getAttribute('name')=='name'){
            var cid=find_channel_block (sp);               
         	cid.getElementsByClassName('ch_name')[0].innerHTML='<h4>'+ input.value +'</h4>';
        }  
        
        if (sp.nextElementSibling.className=='error') {
          	sp.parentNode.removeChild(sp.nextElementSibling);
        }

		input.parentNode.removeChild(input);
        sp.className='glyphicon glyphicon-pencil edit';
        sp.setAttribute('onclick','editChannel(this)');
	}
	else {
		var errorText = document.createElement('span');
        sp.parentNode.insertBefore(errorText,sp.nextElementSibling);
        errorText.className='error';
        errorText.innerHTML = '<br>' + message.replace(/(^\s+|\s+$)/g,'');
	}
}

function runChannelPhase1 (btn) {

	/* При запуске канала, прячем кнопки редактирования */
    var channel_block = find_channel_block (btn);
    
    if (channel_block.getElementsByClassName('ch_info')[0]){
        var elems = channel_block.getElementsByClassName('ch_info')[0].childNodes;
        var editBtns = channel_block.getElementsByClassName('edit');
        
        [].forEach.call(elems, function(elem) {
            if (elem.className && ~elem.className.indexOf('edit')) {
    	        elem.className='glyphicon glyphicon-pencil edit hiden-element';	
    	    }
        });
    }
    
    /* Меняем статусы кнопок */
    channel_block.getElementsByClassName('play')[0].className='btn btn-default btn-green play disabled';
    channel_block.getElementsByClassName('play')[0].removeAttribute('onclick');
    channel_block.getElementsByClassName('delete')[0].className='btn btn-default delete disabled';
    channel_block.getElementsByClassName('delete')[0].removeAttribute('onclick');

    /* Запускаем progress bar */

    var url = '/run_channel_phase1/'+ channel_block.id;
    ajax ('GET',url,function(){ 

        channel_block.getElementsByClassName('ch_status')[0].innerHTML=this;
        /* Отправляем запрос на старт ffmpeg */
        runChannelPhase2(channel_block); 
    });


}

function runChannelPhase2(chb){

    var url = '/run_channel_phase2/'+ chb.id;
    
    ajax ('GET',url,function(){ 
        /* По получении ответа, отправляем запрос на выгрузку лога, меняем статус */ 
        if (this.replace(/\s+/g, '')=='done') {
            chb.style.background='#94E498';
            chb.getElementsByClassName('ch_status')[0].innerHTML='<h4>&nbsp;&nbsp;&nbsp;Запущен</h4>';
            chb.getElementsByClassName('stop')[0].className='btn btn-default stop';
            chb.getElementsByClassName('stop')[0].setAttribute('onclick','stopChannelPhase1(this)'); 
        }
        else {
            chb.style.background='#C8826F';
            chb.getElementsByClassName('ch_status')[0].innerHTML='<h4>&nbsp;&nbsp;&nbsp;&nbsp;Ошибка</h4>';
            chb.getElementsByClassName('play')[0].className='btn btn-default play';
            chb.getElementsByClassName('play')[0].setAttribute('onclick','runChannelPhase1(this)');
            chb.getElementsByClassName('delete')[0].className='btn btn-default delete';
            chb.getElementsByClassName('delete')[0].setAttribute('onclick','deleteChannelPhase1(this)');


            if (chb.getElementsByClassName('ch_info')[0]){
                var elems = chb.getElementsByClassName('ch_info')[0].childNodes;
                var editBtns = chb.getElementsByClassName('edit');

                [].forEach.call(elems, function(elem) {
                    if (elem.className && ~elem.className.indexOf('edit')) {
                        elem.className='glyphicon glyphicon-pencil edit';
                    }
                });

            }

        }
         
        runChannelPhase3(chb); 
                
    });
}

function runChannelPhase3(cb){
    var url = '/run_channel_phase3/'+ cb.id;
    
    /* Получаем лог */
    ajax ('GET',url,function(){

        if (cb.getElementsByClassName('log_text')[0]){
            cb.getElementsByClassName('log_text')[0].innerHTML=this;            
        }        
        
    });
    
}

function stopChannelPhase1 (btn) {

	/* После остановки канал можно снова удалять или редактировать */
    var channel_block = find_channel_block (btn);
        
    /* И делаем кнопку отключения не активной */
    
    channel_block.getElementsByClassName('stop')[0].className='btn btn-default stop disabled';
    channel_block.getElementsByClassName('stop')[0].removeAttribute('onclick');
    
    var url = '/stop_channel_phase1/'+ channel_block.id;

    ajax ('GET',url,function(){ 
    	channel_block.getElementsByClassName('ch_status')[0].innerHTML=this;
        /* Отправляем запрос на Остановку ffmpeg */
        stopChannelPhase2(channel_block); 

    });
}

function stopChannelPhase2(chb){

    var url = '/stop_channel_phase2/'+ chb.id;
    
    ajax ('GET',url,function(){ 
        /* По получении ответа, проверяем ошибки, меняем статус */ 
        
        if (this.replace(/\s+/g, '')=='done') {
            chb.style.background='#C4C8EB'; 
        }
        else {
            chb.style.background='#C8826F';
        }
        
        /* активируем кнопки запуска */
        chb.getElementsByClassName('ch_status')[0].innerHTML='<h4>Остановлен</h4>';
        chb.getElementsByClassName('play')[0].className='btn btn-default play';
        chb.getElementsByClassName('play')[0].setAttribute('onclick','runChannelPhase1(this)');
        chb.getElementsByClassName('delete')[0].className='btn btn-default delete';
        chb.getElementsByClassName('delete')[0].setAttribute('onclick','deleteChannelPhase1(this)');

        /* и редактирования канала */
        if (chb.getElementsByClassName('ch_info')[0]){
            var elems = chb.getElementsByClassName('ch_info')[0].childNodes;
            var editBtns = chb.getElementsByClassName('edit');

            [].forEach.call(elems, function(elem) {
                if (elem.className && ~elem.className.indexOf('edit')) {
                    elem.className='glyphicon glyphicon-pencil edit';
                }
            });
        }
        
        stopChannelPhase3(chb);    
             
    });
}

function stopChannelPhase3(cb){
    var url = '/stop_channel_phase3/'+ cb.id;
    
    /* Получаем лог */ 
    ajax ('GET',url,function(){ 

        if (cb.getElementsByClassName('log_text')[0]) {
            /* Отправляем запрос на лог*/
            cb.getElementsByClassName('log_text')[0].innerHTML=this;        
        }
        
    });
        
}


function deleteChannelPhase1 (btn) {

    var channel=find_channel_block(btn);
    //var url = '/delete_channel_ask/'+ channel.id + '/' + name +'/' + span.previousElementSibling.value;
    var url = '/delete_channel_ask/';
    ajax ('GET',url,function(){ 
    	channel.getElementsByClassName('ch_face')[0].style.display='none';
    	if (channel.getElementsByClassName('ch_info')[0]) {
    		channel.removeChild(channel.getElementsByClassName('ch_info')[0]);
    		channel.removeChild(channel.getElementsByClassName('status')[0]);
    	}    	
    	channel.innerHTML+=this;
    });

}

function noConfirm (btn) {
    var channel=find_channel_block(btn);
    btn.parentNode.parentNode.removeChild(btn.parentNode);
    var face = channel.getElementsByClassName('ch_face')[0];
    face.style.display='block';
    face.getElementsByClassName('ch_down')[0].innerHTML='<span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>';
    face.getElementsByClassName('ch_down')[0].setAttribute('onclick','showInfo(this)');
}

function yesConfirm (btn) {
    var channel=find_channel_block(btn);
    var url = '/delete_channel/' + channel.id;

    ajax ('GET',url,function(){ 
        if(this.replace(/\s+/g, '')=='done') {
            channel.parentNode.removeChild(channel);   
        }      
    });
}

function find_channel_block (startElement) {
	
   	while (startElement.className != 'channel') {
        startElement=startElement.parentNode;
    }
    	
   	return startElement;
     
}


window.onload = function () {
    var inputs=document.getElementsByTagName('input');
	for(z=0;z<inputs.length;z++){
		if (inputs[z].value) {
			fill(inputs[z]);
		}
	}       

}
