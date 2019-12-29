// written by Mitchell Black
/**
 * Paired with a table, it allows the user to select which season they wish to view,
 * setting the display of the desired elements to "table-row" and the rest of the elements to "none".
 * @param  {string} selector_id Element ID of selector to be used.
 * @param  {string} table_id Element ID of table which season selection is to be performed.
 * @param  {number} season_loc Location of element in table which contains season category
 */
function season_selector(selector_id, table_id, season_loc=2){
    let selector = document.getElementById(selector_id);
    let selected_season = selector.value;

    let table = document.getElementById(table_id);
    let outing_data_rows = table.getElementsByClassName("data-row");

    for(var i = 0; i < outing_data_rows.length; i++){
        let data_objects = outing_data_rows[i].getElementsByTagName("td");
        if (selected_season == "All Seasons"){  // for when all seasons is selected
            outing_data_rows[i].style.display = "table-row";
        } else if (data_objects[season_loc].innerHTML == selected_season) {  // for when desired season is selected
            outing_data_rows[i].style.display = "table-row";
        } else {  // for when current season is not this one
            outing_data_rows[i].style.display = "none";
        }
    }
}