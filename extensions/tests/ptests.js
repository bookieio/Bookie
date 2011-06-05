if (phantom.state.length === 0) {
  if(phantom.args.length === 0 || phantom.args.length > 2) {
    console.log("Simple QUnit test runner for phantom.js");
    console.log('Usage: testrunner.js url_to_test_file.html');
    console.log('Accepts: http://example.com/file.html and file://`pwd`/test.html');
    phantom.exit();
  } else {
    phantom.state = "run-qunit";
    phantom.open(phantom.args[0]);
  }
} else {
  console.log("Running tests");
  setInterval(function() {
    var result_el = document.getElementById('qunit-testresult');
    if(typeof result_el !== 'undefined') {
      try {
        var passed = result_el.getElementsByClassName('passed')[0].innerHTML;
        var total = result_el.getElementsByClassName('total')[0].innerHTML;
        var failed = result_el.getElementsByClassName('failed')[0].innerHTML;
      } catch(e) {
        // SHHHHHH
      }
      console.log('Passed: '+passed + ', Failed: '+ failed + ' Total: '+ total);
      if(parseInt(failed,10) > 0) {
        phantom.exit(1);
      } else {
        phantom.exit(0);
      }
    }
  }, 1000);
}
