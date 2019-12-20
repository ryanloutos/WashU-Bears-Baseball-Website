$(document).ready(function() {

    //This function adjusts the subforms when a row is deleted
    function adjustIndices(deleteIndex) {

        //Gets the list of subforms
        var $forms = $('.subform')

        //Iterates through all of the subforms
        $forms.each(function(i) {

            var $form = $(this);
            var index = $form.attr('data-index');

            //sets the updated index for the subform if needed
            var newIndex = index - 1;

            //if subform occurs higher up then return
            if (index < deleteIndex) {
                return true;
            }

            //set the attributes of the subforms with the new index
            $form.attr('id', $form.attr('id').replace(index, newIndex));
            $form.attr('data-index', $form.attr('data-index').replace(index, newIndex));

            //set each of the inputs in the subform with the new index
            $form.find('input').each(function(j) {
                var $item = $(this);
                $item.attr('id', $item.attr('id').replace(index, newIndex));
                $item.attr('name', $item.attr('name').replace(index, newIndex));
            });
            $form.find('select').each(function(j) {
                var $item = $(this);
                $item.attr('id', $item.attr('id').replace(index, newIndex));
                $item.attr('name', $item.attr('name').replace(index, newIndex));
            });
            $form.find('a').each(function(idx) {
                var $item = $(this);
                $item.attr('data-index', newIndex);
            });

            //set pitch# correctly
            $form.find("td:first-child").text(newIndex+1);
        });
    }

    //this function copies the form and appends a new one with the appropriate attributes
    $('#add').click(function addForm() {
        //Get Last index
        var $lastForm = $('.subform').last();

        //sets newIndex 
        if ($lastForm.length > 0) {
            newIndex = parseInt($lastForm.data('index')) + 1;
        }
        else {
            newIndex=0;
        }

        // Maximum of 150 subforms
        if (newIndex > 150) {
            console.log('[WARNING] Reached maximum number of elements');
            return;
        }

        //clone the first subform which will always be there
        var $newForm = $('#pitch-0-form').clone();

        //set the appropriate attributes so subform works
        $newForm.attr('id', 'pitch-'+newIndex+'-form');
        $newForm.attr('data-index', newIndex);

        // looks for the different DOM form elements and updates attributes
        $newForm.find('input').each(function(idx) {
            var $item = $(this);
            $item.attr('id', $item.attr('id').replace('0', newIndex));
            $item.attr('name', $item.attr('name').replace('0', newIndex));
        });
        $newForm.find('select').each(function(idx) {
            var $item = $(this);
            $item.attr('id', $item.attr('id').replace('0', newIndex));
            $item.attr('name', $item.attr('name').replace('0', newIndex));
        });
        $newForm.find('a').each(function(idx) {
            var $item = $(this);
            $item.attr('data-index', newIndex);
        });

        //append to the end of the table
        $("#table > tbody").append($newForm);

        //update pitch type 
        $newForm.find("td:first-child").text(newIndex+1);

        $newForm.addClass('subform');
    });

    //delete a row
    $(document).on('click', '.delete', function () {

        //get the index of this row
        var deleteIndex = $(this).attr('data-index');

        //get the form associated with which delete button was pressed
        var $deleteForm = $('tr[class=subform][data-index='+deleteIndex+']');

        //adjust the indices of each of the existing rows
        adjustIndices(deleteIndex);

        //remove the subform from the table
        $deleteForm.remove();
    });
});