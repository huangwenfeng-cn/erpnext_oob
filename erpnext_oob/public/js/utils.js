frappe.provide("erpnext_oob.utils")

$.extend(erpnext_oob.utils, {
    switch_to_excel_download: function(frm, table_field){
        let grid = frm.fields_dict[table_field].grid; 
        let downloadButton = grid.wrapper.find(".grid-download");
        if (downloadButton.length) { // Check if the button exists
            downloadButton.off('click').on("click", function(event) {
                event.preventDefault(); // Prevent the default download
                export_excel(frm, grid);
            })
        }
    }
})

export_excel = function(frm, grid) {
    let title = grid.df.label || frappe.model.unscrub(grid.df.fieldname);      
    var data = [];
    var docfields = [];
    data.push([__("Bulk Edit {0}", [title])]);
    data.push([]);
    data.push([]);
    data.push([]);
    data.push([__("The CSV format is case sensitive")]);
    data.push([__("Do not edit headers which are preset in the template")]);
    data.push(["------"]);
    $.each(frappe.get_meta(grid.df.options).fields, (i, df) => {
        // don't include the read-only field in the template
        if (frappe.model.is_value_type(df.fieldtype)) {
            data[1].push(__(df.label));
            data[2].push(df.fieldname);
            let description = (df.description || "") + " ";
            if (df.fieldtype === "Date") {
                description += frappe.boot.sysdefaults.date_format;
            }
            data[3].push(__(description));
            docfields.push(df);
        }
    });

    // add data
    $.each(frm.doc[grid.df.fieldname] || [], (i, d) => {
        var row = [];
        $.each(data[2], (i, fieldname) => {
            var value = d[fieldname];

            // format date
            if (docfields[i].fieldtype === "Date" && value) {
                value = frappe.datetime.str_to_user(value);
            }

            row.push(value || "");
        });
        data.push(row);
    });
    let method = "/api/method/erpnext_oob.api.export_excel";
    open_url_post(method, {
        data: data,
        filename: title || frm.docname,
    });
}