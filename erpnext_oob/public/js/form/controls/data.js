//允许翻译的字段，鼠标悬停显示翻译后的值，
//直接在字段中显示翻译后的值影响面太广，不确定有哪些负面影响，所以注释掉了代码
frappe.ui.form.ControlData = class ControlData extends frappe.ui.form.ControlData {
	set_formatted_input(value) {		
		if (value && this.df.translatable === 1){			
			this.$input_wrapper.attr("title", __(value));
			// if (!this.title_value_map) {
			// 	this.title_value_map = {};
			// }
			// let translated_text = __(value);
			// this.title_value_map[translated_text] = value;
			// value = translated_text;
		}

		super.set_formatted_input(value);		
	}

	// get_input_value() {
	// 	if (this.$input) {
	// 		const input_value = this.$input.val();
	// 		return this.title_value_map?.[input_value] || input_value;
	// 	}
	// 	return null;
	// }
}