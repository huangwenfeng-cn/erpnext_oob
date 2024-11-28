// frappe.ui.form.add_options = function (input, options_list) {
// 	let $select = $(input);
// 	if (!Array.isArray(options_list)) {
// 		return $select;
// 	}
// 	// create options
// 	for (var i = 0, j = options_list.length; i < j; i++) {
// 		var v = options_list[i];
// 		var value = null;
// 		var label = null;
// 		if (!is_null(v)) {
// 			var is_value_null = is_null(v.value);
// 			var is_label_null = is_null(v.label);
// 			var is_disabled = Boolean(v.disabled);
// 			var is_selected = Boolean(v.selected);

// 			if (is_value_null && is_label_null) {
// 				//支持分号(;)分隔的值与标签，以解决下拉值一词多义问题
// 				if (v && typeof v ==='string' && v.includes(";")) {
// 					const value_arr = v.split(";");
// 					value = value_arr[0];
// 					label = __(value_arr.slice(-1)[0]);
// 				} else {
// 					value = v;
// 					label = __(v);
// 				}
// 			} else {
// 				value = is_value_null ? "" : v.value;
// 				label = is_label_null ? __(value) : __(v.label);
// 			}
// 		}

// 		$("<option>")
// 			.html(cstr(label))
// 			.attr("value", value)
// 			.prop("disabled", is_disabled)
// 			.prop("selected", is_selected)
// 			.appendTo($select.get(0));
// 	}
// 	// select the first option
// 	$select.get(0).selectedIndex = 0;
// 	$select.trigger("select-change");
// 	return $select;
// };

// // 支持用;分隔的值与标签选项，通过自定义选项，实现一词多义翻译
// (function($) {
// 	$.fn.add_options = function(options_list) {
// 		// create options
// 		for(var i=0, j=options_list.length; i<j; i++) {
// 			var v = options_list[i];
// 			var value = null;
// 			var label = null;
// 			if (!is_null(v)) {
// 				var is_value_null = is_null(v.value);
// 				var is_label_null = is_null(v.label);
// 				var is_disabled = Boolean(v.disabled);

// 				if (is_value_null && is_label_null) {
// 					//支持分号(;)分隔的值与标签，以解决下拉值一词多义问题
// 					if (v && typeof v ==='string' && v.includes(";")) {
// 						const value_arr = v.split(";");
// 						value = value_arr[0];
// 						label = __(value_arr.slice(-1)[0]);
// 					} else {
// 						value = v;
// 						label = __(v);
// 					}
// 				} else {
// 					value = is_value_null ? "" : v.value;
// 					label = is_label_null ? __(value) : __(v.label);
// 				}
// 			}

// 			$('<option>').html(cstr(label))
// 				.attr('value', value)
// 				.prop('disabled', is_disabled)
// 				.appendTo(this);
// 		}
// 		// select the first option
// 		this.selectedIndex = 0;
// 		$(this).trigger('select-change');
// 		return $(this);
// 	};
// 	$.fn.set_working = function() {
// 		this.prop('disabled', true);
// 	};
// 	$.fn.done_working = function() {
// 		this.prop('disabled', false);
// 	};

// 	let original_val = $.fn.val;
// 	$.fn.val = function() {
// 		let result = original_val.apply(this, arguments);
// 		if (arguments.length > 0) $(this).trigger('select-change');
// 		return result;
// 	};
// })(jQuery);