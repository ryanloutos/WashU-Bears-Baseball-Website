/**
 * @param  {string} table_id Id of table to be sorted
 * @param  {string} div_id ID of div containing inputs
 * @param  {number} col Number of the column to be sorted by starting with 0
 */
function checkbox_table(table_id, div_id, col){

    // Get currently selected values
    let checkbox_div = document.getElementById(div_id);
    let inputs = checkbox_div.getElementsByTagName("input");
    let selected_values = [];
    for(var i = 0; i < inputs.length; i++){
        if(inputs[i].checked){
            selected_values.push(inputs[i].value);
        }
    }

    // Gets which row of which table we will be sorting
    let data_table = document.getElementById(table_id);
    let table_data_rows = data_table.getElementsByClassName("data-row");

    // Loop through data-rows to determine behavior
    for(var i = 0; i < table_data_rows.length; i++){
        if(selected_values.length == 0){ // no values selected so all visible
            table_data_rows[i].style.display = "table-row";
        } else{
            let checkbox_desired_row = table_data_rows[i].getElementsByTagName("td")[col];
            if(selected_values.includes(checkbox_desired_row.innerHTML)){
                table_data_rows[i].style.display = "table-row";
            } else {
                table_data_rows[i].style.display = "none";
            }
        }
    }

}