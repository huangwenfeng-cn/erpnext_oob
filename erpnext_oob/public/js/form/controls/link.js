
// 修改link类型数据的翻译，主要就是添加了一个方法set_formatted_input，给input设置值的时候设置翻译过后的值
// 然后在获取焦点和失去焦点的时候取值逻辑修改一下
frappe.ui.form.ControlLink = class ControlLink extends frappe.ui.form.ControlLink {
	make_input() {
		var me = this;
		$(`<div class="link-field ui-front" style="position: relative;">
			<input type="text" class="input-with-feedback form-control">
			<span class="link-btn">
				<a class="btn-open no-decoration" title="${__("Open Link")}">
					${frappe.utils.icon("arrow-right", "xs")}
				</a>
			</span>
		</div>`).prependTo(this.input_area);
		this.$input_area = $(this.input_area);
		this.$input = this.$input_area.find("input");
		this.$link = this.$input_area.find(".link-btn");
		this.$link_open = this.$link.find(".btn-open");
		this.set_input_attributes();
		this.$input.on("focus", function () {
			setTimeout(function () {
				if (me.$input.val() && me.get_options()) {
					let doctype = me.get_options();
					// fisher 修改取值逻辑，直接从doc中取，不从input框中取了
					let real_value = me.doc ? me.doc[me.df['fieldname']] : me.$input.attr("data-value")
					let name = real_value ? real_value : me.get_input_value();
					//fisher 结束修改
					me.$link.toggle(true);
					me.$link_open.attr("href", frappe.utils.get_form_link(doctype, name));
				}

				if (!me.$input.val()) {
					me.$input.val("").trigger("input");

					// hide link arrow to doctype if none is set
					me.$link.toggle(false);
				}
			}, 500);
		});
		this.$input.on("blur", function () {
			// if this disappears immediately, the user's click
			// does not register, hence timeout
			setTimeout(function () {
				me.$link.toggle(false);
			}, 500);
		});
		this.$input.attr("data-target", this.df.options);
		this.input = this.$input.get(0);
		this.has_input = true;
		this.translate_values = true;
		this.setup_buttons();
		this.setup_awesomeplete();
		this.bind_change_event();
	}

	setup_awesomeplete() {
		let me = this;

		this.$input.cache = {};

		this.awesomplete = new Awesomplete(me.input, {
			tabSelect: true,
			minChars: 0,
			maxItems: 99,
			autoFirst: true,
			list: [],
			replace: function (item) {
				// Override Awesomeplete replace function as it is used to set the input value
				// https://github.com/LeaVerou/awesomplete/issues/17104#issuecomment-359185403
				this.input.value = me.get_translated(item.label || item.value);
			},
			data: function (item) {
				return {
					label: me.get_translated(item.label || item.value),
					value: item.value,
				};
			},
			filter: function () {
				return true;
			},
			item: function (item) {
				let d = this.get_item(item.value);
				if (!d.label) {
					d.label = d.value;
				}

				let _label = me.get_translated(d.label);
				let html = d.html || "<strong>" + _label + "</strong>";
				if (
					d.description &&
					// for title links, we want to inlude the value in the description
					// because it will not visible otherwise
					(me.is_title_link() || d.value !== d.description)
				) {
					html += '<br><span class="small">' + __(d.description) + "</span>";
				}
				return $("<li></li>")
					.data("item.autocomplete", d)
					.prop("aria-selected", "false")
					.html(`<a><p title="${frappe.utils.escape_html(_label)}">${html}</p></a>`)
					.get(0);
			},
			sort: function () {
				return 0;
			},
		});

		this.custom_awesomplete_filter && this.custom_awesomplete_filter(this.awesomplete);

		this.$input.on(
			"input",
			frappe.utils.debounce(function (e) {
				var doctype = me.get_options();
				if (!doctype) return;
				if (!me.$input.cache[doctype]) {
					me.$input.cache[doctype] = {};
				}

				var term = e.target.value;

				if (me.$input.cache[doctype][term] != null) {
					// immediately show from cache
					me.awesomplete.list = me.$input.cache[doctype][term];
				}
				var args = {
					txt: term,
					doctype: doctype,
					ignore_user_permissions: me.df.ignore_user_permissions,
					reference_doctype: me.get_reference_doctype() || "",
					page_length: cint(frappe.boot.sysdefaults?.link_field_results_limit) || 10,
				};

				me.set_custom_query(args);

				frappe.call({
					type: "POST",
					method: "frappe.desk.search.search_link",
					no_spinner: true,
					args: args,
					callback: function (r) {
						if (!window.Cypress && !me.$input.is(":focus")) {
							return;
						}
						r.message = me.merge_duplicates(r.message);

						// show filter description in awesomplete
						let filter_string = me.df.filter_description
							? me.df.filter_description
							: args.filters
							? me.get_filter_description(args.filters)
							: null;
						if (filter_string) {
							r.message.push({
								html: `<span class="text-muted" style="line-height: 1.5">${filter_string}</span>`,
								value: "",
								action: () => {},
							});
						}

						if (!me.df.only_select) {
							if (frappe.model.can_create(doctype)) {
								// new item
								r.message.push({
									html:
										"<span class='link-option'>" +
										"<i class='fa fa-plus' style='margin-right: 5px;'></i> " +
										__("Create a new {0}", [__(me.get_options())]) +
										"</span>",
									label: __("Create a new {0}", [__(me.get_options())]),
									value: "create_new__link_option",
									action: me.new_doc,
								});
							}

							//custom link actions
							let custom__link_options =
								frappe.ui.form.ControlLink.link_options &&
								frappe.ui.form.ControlLink.link_options(me);

							if (custom__link_options) {
								r.message = r.message.concat(custom__link_options);
							}

							// advanced search
							if (locals && locals["DocType"]) {
								// not applicable in web forms
								r.message.push({
									html:
										"<span class='link-option'>" +
										"<i class='fa fa-search' style='margin-right: 5px;'></i> " +
										__("Advanced Search") +
										"</span>",
									label: __("Advanced Search"),
									value: "advanced_search__link_option",
									action: me.open_advanced_search,
								});
							}
						}
						me.$input.cache[doctype][term] = r.message;
						me.awesomplete.list = me.$input.cache[doctype][term];
						me.toggle_href(doctype);
					},
				});
			}, 500)
		);

		this.$input.on("blur", function () {
			if (me.selected) {
				me.selected = false;
				return;
			}
			let input_value = me.get_input_value();
			let label = me.get_label_value();
			let last_value = me.last_value || "";
			let last_label = me.label || "";
			// fisher 修改取值对比逻辑， 输入框的值和翻译过后的doc中值不一样，就取输入框的值，一样就取doc中的值						
			let real_value = me.doc ? me.doc[me.df['fieldname']] : me.$input.attr("data-value")
			let value = __(real_value) != input_value ? input_value : real_value
			if (value !== last_value) {
				me.parse_validate_and_set_in_model(value, null, label);
			}		
		});

		this.$input.on("awesomplete-open", () => {
			this.autocomplete_open = true;

			if (!me.get_label_value()) {
				// hide link arrow to doctype if none is set
				me.$link.toggle(false);
			}
		});

		this.$input.on("awesomplete-close", (e) => {
			this.autocomplete_open = false;

			if (!me.get_label_value()) {
				// hide link arrow to doctype if none is set
				me.$link.toggle(false);
			}
		});

		this.$input.on("awesomplete-select", function (e) {
			var o = e.originalEvent;
			var item = me.awesomplete.get_item(o.text.value);

			me.autocomplete_open = false;

			// prevent selection on tab
			let TABKEY = 9;
			if (e.keyCode === TABKEY) {
				e.preventDefault();
				me.awesomplete.close();
				return false;
			}

			if (item.action) {
				item.value = "";
				item.label = "";
				item.action.apply(me);
			}

			// if remember_last_selected is checked in the doctype against the field,
			// then add this value
			// to defaults so you do not need to set it again
			// unless it is changed.
			if (me.df.remember_last_selected_value) {
				frappe.boot.user.last_selected_values[me.df.options] = item.value;
			}

			me.parse_validate_and_set_in_model(item.value, null, item.label);
		});

		this.$input.on("awesomplete-selectcomplete", function (e) {
			let o = e.originalEvent;
			if (o.text.value.indexOf("__link_option") !== -1) {
				me.$input.val("");
			}
		});
	}

	get_filter_description(filters) {
		let doctype = this.get_options();
		let filter_array = [];
		let meta = null;

		frappe.model.with_doctype(doctype, () => {
			meta = frappe.get_meta(doctype);
		});

		// convert object style to array
		if (!Array.isArray(filters)) {
			for (let fieldname in filters) {
				let value = filters[fieldname];
				if (!Array.isArray(value)) {
					value = ['=', value];
				}
				filter_array.push([fieldname, ...value]); // fieldname, operator, value
			}
		} else {
			filter_array = filters;
		}

		// add doctype if missing
		filter_array = filter_array.map(filter => {
			if (filter.length === 3) {
				return [doctype, ...filter]; // doctype, fieldname, operator, value
			}
			return filter;
		});

		function get_filter_description(filter) {
			let doctype = filter[0];
			let fieldname = filter[1];
			let docfield = frappe.meta.get_docfield(doctype, fieldname);
			let label = docfield ? docfield.label : frappe.model.unscrub(fieldname);

			if (docfield && docfield.fieldtype === 'Check') {
				filter[3] = filter[3] ? __('Yes'): __('No');
			}

			if (filter[3] && Array.isArray(filter[3]) && filter[3].length > 5) {
				filter[3] = filter[3].slice(0, 5);
				filter[3].push('...');
			}

			let value = filter[3] == null || filter[3] === ''
				? __('empty')
				: filter[3];

			return [__(label).bold(), __(filter[2]), (Array.isArray(filter[3]) ? String(value.map(v => __(v))) : String(__(value))).bold()].join(' ');
		}

		let filter_string = filter_array
			.map(get_filter_description)
			.join(', ');

		return __('Filters applied for {0}', [filter_string]);
	}

    // fisher 添加的方法
    set_formatted_input(value) {
		var me = this
		me.$input && me.$input.attr("data-value", value === undefined ? '' : value)
		me.$input && me.$input.val(me.format_for_input(__(value)));
		super.set_formatted_input(value);
	}

	// fisher 获取本来的值
	get_value() {
		let me = this
		let real_value = me.doc ? me.doc[me.df['fieldname']] : (me.$input ? me.$input.attr("data-value") : undefined)
		let value = real_value ? real_value : me.get_input_value();
		if(this.get_status()==='Write') {
			return this.parse ? this.parse(value) : value;
		} else {
			return value? value: this.value || null;
		}
	}
}

frappe.ui.form.ControlAutocomplete = class ControlAutocomplete extends frappe.ui.form.ControlAutocomplete {
	setup_awesomplete() {
		const settings = super.setup_awesomplete() || {};
		return Object.assign(settings, {
			filter: function(item, input) {				
				let hay = item.value;
				//fisher 支持中英文检索
				if (__(item.value) != item.value)	hay += __(item.value)
				return Awesomplete.FILTER_CONTAINS(hay, input);
			}
		})
	}
    // fisher 添加的方法
    set_formatted_input(value) {
		var me = this
		value && me.$input && me.$input.attr("data-value", value === undefined ? '' : value)
		value && me.$input && me.$input.val(me.format_for_input(__(value)));
	}

	// fisher 获取本来的值
	get_value() {
		let me = this
		let real_value = me.$input && me.$input.attr("data-value") ? me.$input.attr("data-value") : (me.doc ? me.doc[me.df['fieldname']] : undefined)
		let value = real_value ? real_value : me.get_input_value();
		if(this.get_status()==='Write') {
			return this.parse ? this.parse(value) : value;
		} else {
			return value || undefined;
		}
	}

	get_parsed_value(value) {
		let me = this;
		if (me.doc){
			let real_value = me.$input && me.$input.attr("data-value") ? me.$input.attr("data-value") : (me.doc ? me.doc[me.df['fieldname']] : undefined)
			value = real_value ? real_value : me.get_input_value();
		} else {
			value = super.get_parsed_value(value);
		}
		return value;
	}
}

frappe.ui.form.ControlMultiSelect = class ControlMultiSelect extends frappe.ui.form.ControlMultiSelect {
	get_value() {
		if (this.$input) {
			const label = this.$input.val();	// '进行中,草稿, ';  			  
			// 清理字符串，去除尾随空格并分割成数组  
			const labels = label.trim().split(',').map(label => label.trim());  			  
			// 使用map和find找到对应的value  
			const values = labels.map(label => {  
				const item = this._data?.find(item => item.label === label);  
				return item ? item.value : ''; // 如果没有找到对应的label，则返回空字符串  
			}).filter(value => value !== '');  
			return values && values.length>0 ? values.join(',') : label;  //将values数组转换回逗号分隔的字符串  			
		}
	}
}

frappe.ui.FieldSelect = class FieldSelect extends frappe.ui.FieldSelect {
	//fisher 支持中英文检索
	init(opts) {
		super.init(opts);
		this.awesomplete.filter = function(item, input) {
			if (! input) return
			let hay = item.label + item.value;						
			return Awesomplete.FILTER_CONTAINS(hay, input);
		}
	}
}

// frappe.ui.FieldSelect = MyFieldSelect
