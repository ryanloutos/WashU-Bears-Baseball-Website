/**
 * Reads the currently checked inputs of a certain class name, and returns an array of their value tags
 * @param  {string} input_class String class name of checkbox inputs
 * 
 * @returns {Array} Array containing the db ID's of the seasons currently selected
 */
function get_selected_seasons(input_class){
    let selected_seasons = [];
    document.querySelectorAll("."+input_class).forEach(function(checkbox){
        if(checkbox.checked){
            selected_seasons.push(checkbox.value);
        }
    });

    return selected_seasons;
}

/**
 * Takes in information regarding database values and page elements, and processes the
 * current state of the page to make certain divs visible based on user selection.
 * 
 * @param  {Array} selected_seasons Array of selected season's season id's from DB
 * @param  {string} holder_class String class name of HTML div holder for tables
 * @param  {string} input_class String class name of checkbox inputs
 * @param  {string} id_suffix String suffix of the id's of the holder divs
 * 
 * @returns {boolean} True iff holder for selected seasons exists, and can be made visible. False if
 * holder does not exist, or cannot be made visible.
 */
function show_selected_seasons(selected_seasons, holder_class, input_class, id_suffix){

    // Check for if all seasons selected, or no seasons selected. Both result in displaying
    // all season's data.
    if(selected_seasons.length == 0 || selected_seasons.length == document.querySelectorAll("."+input_class).length){
        // Access all existing holder elements
        holders = document.querySelectorAll("."+holder_class);
        
        // first holder in list should always exist and be all seasons
        holders[0].style.display = "block";

        // for remaining holders, make invisible
        for(let i = 1; i < holders.length; i++){
            holders[i].style.display = "none";
        }

        // Exit the function as all desired jobs have been completed
        // Return true if holder for selected seasons exists, and can be made visible.
        return true;
    }

    // Check all existing holders to see if there is an id match
    let holder_id = generate_holder_id(selected_seasons, id_suffix);

    // State var for if there exists a match in holder ID name
    let match = false;

    // Iterate over all existing table holders for id match
    document.querySelectorAll("."+holder_class).forEach(function(holder){
        // If there is an ID match, make the holder visible. Else make holder invisible.
        if(holder.id == holder_id){
            holder.style.display = "block";
            match = true;
        } else {
            holder.style.display = "none";
        }
    });

    if(match){
        // Return true if holder for selected seasons exists, and can be made visible.
        return true;
    } else {
        // Return false if holder does not exist, and ajax is required
        return false;
    }

}

function generate_holder_id(selected_seasons, id_suffix){
    let holder_id = "";
    selected_seasons.forEach(function(season){
        holder_id += season + "-";
    });
    holder_id += id_suffix;
    return holder_id;
}