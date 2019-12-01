// https://www.rmedgar.com/blog/dynamic_fields_flask_wtf
function addForm() {
    var $templateForm = $('#pitch-_-form');

    if (!$templateForm) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    // Maximum of 150 subforms
    if (newIndex > 150) {
        console.log('[WARNING] Reached maximum number of elements');
        return;
    }

    // Add elements
    var $newForm = $templateForm.clone();

    $newForm.attr('id', 'pitch-'+$newForm+'-form');
    $newForm.data('index', newIndex);

    $newForm.find('input').each(function(idx) {
        var $item = $(this);

        $item.attr('id', $item.attr('id').replace('_', newIndex));
        $item.attr('name', $item.attr('name').replace('_', newIndex));
    });

    $newForm.find('select').each(function(idx) {
        var $item = $(this);

        $item.attr('id', $item.attr('id').replace('_', newIndex));
        $item.attr('name', $item.attr('name').replace('_', newIndex));
    });

    // Append
    $('.table').append($newForm);
    $newForm.addClass('subform');
    $newForm.removeClass('is-hidden');
}

$(document).ready(function() {
    $('#add').click(addForm());
});


//  <div class='is-hidden'>
// <tr id="pitch-_-form" class="is-hidden" data-index="_">
//     <td><input id="pitch-_-pitch_num" name="pitch-_-pitch_num" required size="6" type="text" value="1"></td>
//     <td><input id="pitch-_-batter_id" name="pitch-_-batter_id" required size="6" type="text" value="2"></td>
//     <td><select id="pitch-_-batter_hand" name="pitch-_-batter_hand" required><option selected value="RHH">RHH</option><option value="LHH">LHH</option></select></td>
//     <td><input id="pitch-_-velocity" name="pitch-_-velocity" size="6" type="text" value=""></td>
//     <td><select id="pitch-_-lead_runner" name="pitch-_-lead_runner" required><option selected value="Empty">Empty</option><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></td>
//     <td><input id="pitch-_-time_to_plate" name="pitch-_-time_to_plate" size="6" type="text" value=""></td>
//     <td><select id="pitch-_-pitch_type" name="pitch-_-pitch_type" required><option selected value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="7">7</option></select></td>
//     <td><select id="pitch-_-pitch_result" name="pitch-_-pitch_result" required><option selected value="B">B</option><option value="CS">CS</option><option value="SS">SS</option><option value="F">F</option><option value="IP">IP</option></select></td>
//     <td><input id="pitch-_-hit_spot" name="pitch-_-hit_spot" type="checkbox" value="y"></td>
//     <td><select id="pitch-_-count_balls" name="pitch-_-count_balls" required><option selected value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></td>
//     <td><select id="pitch-_-count_strikes" name="pitch-_-count_strikes" required><option selected value="0">0</option><option value="1">1</option><option value="2">2</option></select></td>
//     <td><select id="pitch-_-result" name="pitch-_-result"><option selected value=""></option><option value="GB">GB</option><option value="FB">FB</option><option value="LD">LD</option><option value="K">K</option><option value="KL">KL</option></select></td>
//     <td><select id="pitch-_-fielder" name="pitch-_-fielder"><option selected value=""></option><option value="P">P</option><option value="C">C</option><option value="1B">1B</option><option value="2B">2B</option><option value="3B">3B</option><option value="SS">SS</option><option value="LF">LF</option><option value="CF">CF</option><option value="RF">RF</option></select></td>
//     <td><input id="pitch-_-hit" name="pitch-_-hit" type="checkbox" value="y"></td>
//     <td><select id="pitch-_-out" name="pitch-_-out"><option selected value=""></option><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></td>
//     <td><input id="pitch-_-inning" name="pitch-_-inning" size="6" type="text" value=""></td>
// </tr>
// </div>