// just a starter test
test("hello", function() {
    ok(false, "world");
});





/**
 * Make sure that once we enable the delete button it's visible
 *
 */
test("delete_button", function() {
    equal($('#delete:visible').length, 0, "Delete button is not visible");
    bookie.ui.enable_delete();
    equal($('#delete:visible').length, 1, "Delete button is visible");
});
