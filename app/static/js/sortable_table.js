// Credit to https://www.w3schools.com/howto/howto_js_sort_table.asp
/** Paired with a table, allows for the table to be sorted by a certian column by clicking that
* column header
* 
* @param  {number} n Column of table to sort by
* @param  {number} tab number of table to be sorted starting at 0
*/
function sortTable(n, tab) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementsByClassName("sortable_table")[tab];
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
            first, which contains table headers): */
            for (i = 1; i < (rows.length - 1); i++) {
                // Start by saying there should be no switching:
                shouldSwitch = false;
                /* Get the two elements you want to compare,
                one from current row and one from the next: */
                x = rows[i].getElementsByTagName("TD")[n];
                y = rows[i + 1].getElementsByTagName("TD")[n];
                /* Check if the two rows should switch place,
                based on the direction, asc or desc: */
                if (dir == "asc") {
                    x_num = Number(x.innerHTML.toLowerCase());
                    y_num = Number(y.innerHTML.toLowerCase());
                    // check to see if comparing numeric values instead or strings
                    if(isNaN(x_num) || isNaN(y_num)){
                        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                            // If so, mark as a switch and break the loop:
                            shouldSwitch = true;
                            break;
                        }
                    } else{
                        if(x_num > y_num){
                            shouldSwitch = true;
                            break;
                        }
                    }
                    
                } else if (dir == "desc") {
                    x_num = Number(x.innerHTML.toLowerCase());
                    y_num = Number(y.innerHTML.toLowerCase());
                    // check to see if comparing numeric values instead or strings
                    if(isNaN(x_num) || isNaN(y_num)){
                        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                            // If so, mark as a switch and break the loop:
                            shouldSwitch = true;
                            break;
                        }
                    } else{
                        if(x_num < y_num){
                            shouldSwitch = true;
                            break;
                        }
                    }
                }
            }
            if (shouldSwitch) {
                /* If a switch has been marked, make the switch
                and mark that a switch has been done: */
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                // Each time a switch is done, increase this count by 1:
                switchcount ++;
            } else {
                /* If no switching has been done AND the direction is "asc",
                set the direction to "desc" and run the while loop again. */
                if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                }
            }
        }
    }