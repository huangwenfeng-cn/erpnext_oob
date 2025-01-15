//允许翻译的字段，显示翻译后的值, 借鉴自link.js
frappe.ui.form.ControlData = class ControlData extends frappe.ui.form.ControlData {
	set_formatted_input(value) {
		if (!this.title_value_map) {
			this.title_value_map = {};
		}
		if (value && this.df.translatable === 1){
			let translated_text = __(value);
			this.title_value_map[translated_text] = value;
			value = translated_text;
		}
		super.set_formatted_input(value);		
	}

	get_input_value() {
		if (this.$input) {
			const input_value = this.$input.val();
			return this.title_value_map?.[input_value] || input_value;
		}
		return null;
	}
}