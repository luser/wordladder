/*
	HUMANIZED MESSAGES 1.0
	idea - http://www.humanized.com/weblog/2006/09/11/monolog_boxes_and_transparent_messages
	home - http://humanmsg.googlecode.com
*/

var humanMsg = {
	setup: function(appendTo, msgOpacity) {
		humanMsg.msgID = 'humanMsg';

		// appendTo is the element the msg is appended to
		if (appendTo == undefined)
			appendTo = 'body';

		// Opacity of the message
		humanMsg.msgOpacity = .8;

		if (msgOpacity != undefined) 
			humanMsg.msgOpacity = parseFloat(msgOpacity);

		// Inject the message structure
		jQuery(appendTo).append('<div id="'+humanMsg.msgID+'" class="humanMsg"><p></p></div>')
	},

	displayMsg: function(msg) {
		if (msg == '')
			return;

		clearTimeout(humanMsg.t2);

		// Inject message
		jQuery('#'+humanMsg.msgID+' p').html(msg);
	
		// Show message
		jQuery('#'+humanMsg.msgID+'').show().animate({ opacity: humanMsg.msgOpacity}, 100);

		// Watch for mouse & keyboard in .2s
		humanMsg.t1 = setTimeout("humanMsg.bindEvents()", 200)
		// Remove message after 1s
		humanMsg.t2 = setTimeout("humanMsg.removeMsg()", 1000)
	},

	bindEvents: function() {
	// Remove message if mouse is moved or key is pressed
		jQuery(window)
			.mousemove(humanMsg.removeMsg)
			.click(humanMsg.removeMsg)
			.keypress(humanMsg.removeMsg)
	},

	removeMsg: function() {
		// Unbind mouse & keyboard
		jQuery(window)
			.unbind('mousemove', humanMsg.removeMsg)
			.unbind('click', humanMsg.removeMsg)
			.unbind('keypress', humanMsg.removeMsg)

		// If message is fully transparent, fade it out
		if (jQuery('#'+humanMsg.msgID).css('opacity') == humanMsg.msgOpacity)
			jQuery('#'+humanMsg.msgID).animate({ opacity: 0 }, 200, function() { jQuery(this).hide() })
	}
};

jQuery(document).ready(function(){
	humanMsg.setup();
})
