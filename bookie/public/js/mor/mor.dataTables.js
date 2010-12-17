/*
 * File:        jquery.dataTables.js
 * Version:     1.5.0
 * CVS:         $Id$
 * Description: Paginate, search and sort HTML tables
 * Author:      Allan Jardine (www.sprymedia.co.uk)
 * Created:     28/3/2008
 * Modified:    $Date$ by $Author$
 * Language:    Javascript
 * License:     GPL v2 or BSD 3 point style
 * Project:     Mtaala
 * Contact:     allan.jardine@sprymedia.co.uk
 * 
 * Copyright 2008-2009 Allan Jardine, all rights reserved.
 *
 * This source file is free software, under either the GPL v2 license or a
 * BSD style license, as supplied with this software.
 * 
 * This source file is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
 * or FITNESS FOR A PARTICULAR PURPOSE. See the license files for details.
 * 
 * For details pleease refer to: http://www.datatables.net
 */

/*
 * When considering jsLint, we need to allow eval() as it it is used for reading cookies and 
 * building the dynamic multi-column sort functions.
 */
/*jslint evil: true, undef: true, browser: true */
/*globals $, jQuery,_fnReadCookie,_fnProcessingDisplay,_fnDraw,_fnSort,_fnReDraw,_fnDetectType,_fnSortingClasses,_fnSettingsFromNode,_fnBuildSearchArray,_fnCalculateEnd,_fnFeatureHtmlProcessing,_fnFeatureHtmlPaginate,_fnFeatureHtmlInfo,_fnFeatureHtmlFilter,_fnFilter,_fnSaveState,_fnFilterColumn,_fnEscapeRegex,_fnFilterComplete,_fnFeatureHtmlLength,_fnGetDataMaster,_fnVisibleToColumnIndex,_fnDrawHead,_fnAddData,_fnGetTrNodes,_fnColumnIndexToVisible,_fnCreateCookie,_fnAddOptionsHtml,_fnMap,_fnClearTable,_fnDataToSearch,_fnReOrderIndex,_fnFilterCustom,_fnVisbleColumns,_fnAjaxUpdate,_fnAjaxUpdateDraw,_fnColumnOrdering,fnGetMaxLenString*/

/**
 * My Notes:
 *  sEcho keeps track of the request order, send this back untouched in the
 *  response
 *
 *  For paging need all of these: 
 *          mor_AjaxResponse::Output(true
            , ''
            , array(
                    'campaign_id' => $campaign_id
                    , 'iTztalRecords' => 100
                    , 'iTotalDisplayRecords' => 100
                    , 'aaData' => $subid_stats_trim)
            , true);


 */


(function($) {
	/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	 * DataTables variables
	 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
	
	/*
	 * Variable: dataTableSettings
	 * Purpose:  Store the settings for each dataTables instance
	 * Scope:    jQuery.fn
	 */
	$.fn.dataTableSettings = [];
	
	/*
	 * Variable: dataTableExt
	 * Purpose:  Container for customisable parts of DataTables
	 * Scope:    jQuery.fn
	 */
	$.fn.dataTableExt = {};
	var _oExt = $.fn.dataTableExt; /* Short reference for fast internal lookup */
	
	
	/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	 * DataTables extensible objects
	 * 
	 * The _oExt object is used to provide an area where user dfined plugins can be 
	 * added to DataTables. The following properties of the object are used:
	 *   oApi - Plug-in API functions
	 *   aTypes - Auto-detection of types
	 *   oSort - Sorting functions used by DataTables (based on the type)
	 *   oPagination - Pagination functions for different input styles
	 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
	
	/*
	 * Variable: sVersion
	 * Purpose:  Version string for plug-ins to check compatibility
	 * Scope:    jQuery.fn.dataTableExt
	 */
	_oExt.sVersion = "1.5.0";
	
	/*
	 * Variable: iApiIndex
	 * Purpose:  Index for what 'this' index API functions should use
	 * Scope:    jQuery.fn.dataTableExt
	 */
	_oExt.iApiIndex = 0;
	
	/*
	 * Variable: oApi
	 * Purpose:  Container for plugin API functions
	 * Scope:    jQuery.fn.dataTableExt
	 */
	_oExt.oApi = { };
	
	/*
	 * Variable: aFiltering
	 * Purpose:  Container for plugin filtering functions
	 * Scope:    jQuery.fn.dataTableExt
	 */
	_oExt.afnFiltering = [ ];

     
	
	/*
	 * Variable: aoFeatures
	 * Purpose:  Container for plugin function functions
	 * Scope:    jQuery.fn.dataTableExt
	 * Notes:    Array of objects with the following parameters:
	 *   fnInit: Function for initialisation of Feature. Takes oSettings and returns node
	 *   cFeature: Character that will be matched in sDom - case sensitive
	 *   sFeature: Feature name - just for completeness :-)
	 */
	_oExt.aoFeatures = [ ];
	
	/*
	 * Variable: ofnSearch
	 * Purpose:  Container for custom filtering functions
	 * Scope:    jQuery.fn.dataTableExt
	 * Notes:    This is an object (the name should match the type) for custom filtering function,
	 *   which can be used for live DOM checking or formatted text filtering
	 */
	_oExt.ofnSearch = { };
	
	/*
	 * Variable: oPagination
	 * Purpose:  Container for the various type of pagination that dataTables supports
	 * Scope:    jQuery.fn.dataTableExt
	 */
	_oExt.oPagination = {
		/*
		 * Variable: two_button
		 * Purpose:  Standard two button (forward/back) pagination
	 	 * Scope:    jQuery.fn.dataTableExt.oPagination
		 */
		"two_button": {
			/*
			 * Function: oPagination.two_button.fnInit
			 * Purpose:  Initalise dom elements required for pagination with forward/back buttons only
			 * Returns:  -
	 		 * Inputs:   object:oSettings - dataTables settings object
			 *           function:fnCallbackDraw - draw function which must be called on update
			 */
			"fnInit": function ( oSettings, fnCallbackDraw )
			{
				var nPaging = oSettings.anFeatures.p;
				
				/* Store the next and previous elements in the oSettings object as they can be very
				 * usful for automation - particularly testing
				 */
				oSettings.nPrevious = document.createElement( 'div' );
				oSettings.nNext = document.createElement( 'div' );
				
				if ( oSettings.sTableId !== '' )
				{
					nPaging.setAttribute( 'id', oSettings.sTableId+'_paginate' );
					oSettings.nPrevious.setAttribute( 'id', oSettings.sTableId+'_previous' );
					oSettings.nNext.setAttribute( 'id', oSettings.sTableId+'_next' );
				}
				
				oSettings.nPrevious.className = "paginate_disabled_previous";
				oSettings.nNext.className = "paginate_disabled_next";
				
				oSettings.nPrevious.title = oSettings.oLanguage.oPaginate.sPrevious;
				oSettings.nNext.title = oSettings.oLanguage.oPaginate.sNext;
				
				nPaging.appendChild( oSettings.nPrevious );
				nPaging.appendChild( oSettings.nNext );
				$(nPaging).insertAfter( oSettings.nTable );
				
				$(oSettings.nPrevious).click( function() {
					oSettings._iDisplayStart -= oSettings._iDisplayLength;
					
					/* Correct for underrun */
					if ( oSettings._iDisplayStart < 0 )
					{
					  oSettings._iDisplayStart = 0;
					}
					
					fnCallbackDraw( oSettings );
				} );
				
				$(oSettings.nNext).click( function() {
					/* Make sure we are not over running the display array */
					if ( oSettings._iDisplayStart + oSettings._iDisplayLength < oSettings.fnRecordsDisplay() )
					{
						oSettings._iDisplayStart += oSettings._iDisplayLength;
					}
					
					fnCallbackDraw( oSettings );
				} );
				
				/* Take the brutal approach to cancelling text selection */
				$(oSettings.nPrevious).bind( 'selectstart', function () { return false; } );
				$(oSettings.nNext).bind( 'selectstart', function () { return false; } );
			},
			
			/*
			 * Function: oPagination.two_button.fnUpdate
			 * Purpose:  Update the two button pagination at the end of the draw
			 * Returns:  -
	 		 * Inputs:   object:oSettings - dataTables settings object
			 *           function:fnCallbackDraw - draw function which must be called on update
			 */
			"fnUpdate": function ( oSettings, fnCallbackDraw )
			{
				if ( !oSettings.anFeatures.p )
				{
					return;
				}
				
				oSettings.nPrevious.className = 
					( oSettings._iDisplayStart === 0 ) ? 
					"paginate_disabled_previous" : "paginate_enabled_previous";
				
				oSettings.nNext.className = 
					( oSettings.fnDisplayEnd() == oSettings.fnRecordsDisplay() ) ? 
					"paginate_disabled_next" : "paginate_enabled_next";
			}
		},
		
		
		/*
		 * Variable: iFullNumbersShowPages
		 * Purpose:  Change the number of pages which can be seen
	 	 * Scope:    jQuery.fn.dataTableExt.oPagination
		 */
		"iFullNumbersShowPages": 5,
		
		/*
		 * Variable: full_numbers
		 * Purpose:  Full numbers pagination
	 	 * Scope:    jQuery.fn.dataTableExt.oPagination
		 */
		"full_numbers": {
			/*
			 * Function: oPagination.full_numbers.fnInit
			 * Purpose:  Initalise dom elements required for pagination with a list of the pages
			 * Returns:  -
	 		 * Inputs:   object:oSettings - dataTables settings object
			 *           function:fnCallbackDraw - draw function which must be called on update
			 */
			"fnInit": function ( oSettings, fnCallbackDraw )
			{
				var nPaging = oSettings.anFeatures.p;
				var nFirst = document.createElement( 'span' );
				var nPrevious = document.createElement( 'span' );
				var nList = document.createElement( 'span' );
				var nNext = document.createElement( 'span' );
				var nLast = document.createElement( 'span' );
				
				nFirst.innerHTML = oSettings.oLanguage.oPaginate.sFirst;
				nPrevious.innerHTML = oSettings.oLanguage.oPaginate.sPrevious;
				nNext.innerHTML = oSettings.oLanguage.oPaginate.sNext;
				nLast.innerHTML = oSettings.oLanguage.oPaginate.sLast;
				
				nFirst.className = "paginate_button first";
				nPrevious.className = "paginate_button previous";
				nNext.className="paginate_button next";
				nLast.className = "paginate_button last";
				
				if ( oSettings.sTableId !== '' )
				{
					nPaging.setAttribute( 'id', oSettings.sTableId+'_paginate' );
					nPrevious.setAttribute( 'id', oSettings.sTableId+'_previous' );
					nPrevious.setAttribute( 'id', oSettings.sTableId+'_previous' );
					nNext.setAttribute( 'id', oSettings.sTableId+'_next' );
					nLast.setAttribute( 'id', oSettings.sTableId+'_last' );
				}
				
				nPaging.appendChild( nFirst );
				nPaging.appendChild( nPrevious );
				nPaging.appendChild( nList );
				nPaging.appendChild( nNext );
				nPaging.appendChild( nLast );
				
				$(nFirst).click( function () {
					oSettings._iDisplayStart = 0;
					fnCallbackDraw( oSettings );
				} );
				
				$(nPrevious).click( function() {
					oSettings._iDisplayStart -= oSettings._iDisplayLength;
					
					/* Correct for underrun */
					if ( oSettings._iDisplayStart < 0 )
					{
					  oSettings._iDisplayStart = 0;
					}
					
					fnCallbackDraw( oSettings );
				} );
				
				$(nNext).click( function() {
					/* Make sure we are not over running the display array */
					if ( oSettings._iDisplayStart + oSettings._iDisplayLength < oSettings.fnRecordsDisplay() )
					{
						oSettings._iDisplayStart += oSettings._iDisplayLength;
					}
					
					fnCallbackDraw( oSettings );
				} );
				
				$(nLast).click( function() {
					var iPages = parseInt( (oSettings.fnRecordsDisplay()-1) / oSettings._iDisplayLength, 10 ) + 1;
					oSettings._iDisplayStart = (iPages-1) * oSettings._iDisplayLength;
					
					fnCallbackDraw( oSettings );
				} );
				
				/* Take the brutal approach to cancelling text selection */
				$('span', nPaging).bind( 'mousedown', function () { return false; } );
				$('span', nPaging).bind( 'selectstart', function () { return false; } );
				
				oSettings.nPaginateList = nList;
			},
			
			/*
			 * Function: oPagination.full_numbers.fnUpdate
			 * Purpose:  Update the list of page buttons shows
			 * Returns:  -
	 		 * Inputs:   object:oSettings - dataTables settings object
			 *           function:fnCallbackDraw - draw function which must be called on update
			 */
			"fnUpdate": function ( oSettings, fnCallbackDraw )
			{
				if ( !oSettings.anFeatures.p )
				{
					return;
				}
				
				var iPageCount = jQuery.fn.dataTableExt.oPagination.iFullNumbersShowPages;
				var iPageCountHalf = Math.floor(iPageCount / 2);
				var iPages = Math.ceil((oSettings.fnRecordsDisplay()-1) / oSettings._iDisplayLength) + 1;
				var iCurrentPage = Math.ceil(oSettings._iDisplayStart / oSettings._iDisplayLength) + 1;
				var sList = "";
				var iStartButton;
				var iEndButton;
				
				if (iPages < iPageCount)
				{
					iStartButton = 1;
					iEndButton = iPages;
				}
				else
				{
					if (iCurrentPage <= iPageCountHalf)
					{
						iStartButton = 1;
						iEndButton = iPageCount;
					}
					else
					{
						if (iCurrentPage >= (iPages - iPageCountHalf))
						{
							iStartButton = iPages - iPageCount + 1;
							iEndButton = iPages;
						}
						else
						{
							iStartButton = iCurrentPage - Math.ceil(iPageCount / 2) + 1;
							iEndButton = iStartButton + iPageCount - 1;
						}
					}
				}
				
				for ( var i=iStartButton ; i<=iEndButton ; i++ )
				{
					if ( iCurrentPage != i )
					{
						sList += '<span class="paginate_button">'+i+'</span>';
					}
					else
					{
						sList += '<span class="paginate_active">'+i+'</span>';
					}
				}
				
				oSettings.nPaginateList.innerHTML = sList;
				
				/* Take the brutal approach to cancelling text selection */
				$('span', oSettings.nPaginateList).bind( 'mousedown', function () { return false; } );
				$('span', oSettings.nPaginateList).bind( 'selectstart', function () { return false; } );
				
				$('span', oSettings.nPaginateList).click( function() {
					var iTarget = (this.innerHTML * 1) - 1;
					oSettings._iDisplayStart = iTarget * oSettings._iDisplayLength;
					
					fnCallbackDraw( oSettings );
					return false;
				} );
			}
		}
	};
	
	/*
	 * Variable: oSort
	 * Purpose:  Wrapper for the sorting functions that can be used in DataTables
	 * Scope:    jQuery.fn.dataTableExt
	 * Notes:    The functions provided in this object are basically standard javascript sort
	 *   functions - they expect two inputs which they then compare and then return a priority
	 *   result. For each sort method added, two functions need to be defined, an ascending sort and
	 *   a descending sort.
	 */
	_oExt.oSort = {
		/*
		 * text sorting
		 */
		"string-asc": function ( a, b )
		{
			var x = a.toLowerCase();
			var y = b.toLowerCase();
			return ((x < y) ? -1 : ((x > y) ? 1 : 0));
		},
		
		"string-desc": function ( a, b )
		{
			var x = a.toLowerCase();
			var y = b.toLowerCase();
			return ((x < y) ? 1 : ((x > y) ? -1 : 0));
		},
		
		
		/*
		 * html sorting (ignore html tags)
		 */
		"html-asc": function ( a, b )
		{
			var x = a.replace( /<.*?>/g, "" ).toLowerCase();
			var y = b.replace( /<.*?>/g, "" ).toLowerCase();
			return ((x < y) ? -1 : ((x > y) ? 1 : 0));
		},
		
		"html-desc": function ( a, b )
		{
			var x = a.replace( /<.*?>/g, "" ).toLowerCase();
			var y = b.replace( /<.*?>/g, "" ).toLowerCase();
			return ((x < y) ? 1 : ((x > y) ? -1 : 0));
		},
		
		
		/*
		 * date sorting
		 */
		"date-asc": function ( a, b )
		{
			var x = Date.parse( a );
			var y = Date.parse( b );
			
			if ( isNaN( x ) )
			{
    		x = Date.parse( "01/01/1970 00:00:00" );
			}
			if ( isNaN( y ) )
			{
				y =	Date.parse( "01/01/1970 00:00:00" );
			}
			
			return x - y;
		},
		
		"date-desc": function ( a, b )
		{
			var x = Date.parse( a );
			var y = Date.parse( b );
			
			if ( isNaN( x ) )
			{
    		x = Date.parse( "01/01/1970 00:00:00" );
			}
			if ( isNaN( y ) )
			{
				y =	Date.parse( "01/01/1970 00:00:00" );
			}
			
			return y - x;
		},
		
		
		/*
		 * numerical sorting
		 */
		"numeric-asc": function ( a, b )
		{
			var x = a == "-" ? 0 : a;
			var y = b == "-" ? 0 : b;
			return x - y;
		},
		
		"numeric-desc": function ( a, b )
		{
			var x = a == "-" ? 0 : a;
			var y = b == "-" ? 0 : b;
			return y - x;
		}
	};
	
	
	/*
	 * Variable: aTypes
	 * Purpose:  Container for the various type of type detection that dataTables supports
	 * Scope:    jQuery.fn.dataTableExt
	 * Notes:    The functions in this array are expected to parse a string to see if it is a data
	 *   type that it recognises. If so then the function should return the name of the type (a
	 *   corresponding sort function should be defined!), if the type is not recognised then the
	 *   function should return null such that the parser and move on to check the next type.
	 *   Note that ordering is important in this array - the functions are processed linearly,
	 *   starting at index 0.
	 */
	_oExt.aTypes = [
		/*
		 * Function: -
		 * Purpose:  Check to see if a string is numeric
		 * Returns:  string:'numeric' or null
		 * Inputs:   string:sText - string to check
		 */
		function ( sData )

		{
			/* Snaity check that we are dealing with a string or quick return for a number */
			if ( typeof sData == 'number' )
			{
				return 'numeric';
			}
            else if ( sData == null) {
                return null;
            }
			else if ( typeof sData.charAt != 'function' )
			{
				return null;
			}
			
			var sValidFirstChars = "0123456789-";
			var sValidChars = "0123456789.";
			var Char;
			var bDecimal = false;
			
			/* Check for a valid first char (no period and allow negatives) */
			Char = sData.charAt(0); 
			if (sValidFirstChars.indexOf(Char) == -1) 
			{
				return null;
			}
			
			/* Check all the other characters are valid */
			for ( var i=1 ; i<sData.length ; i++ ) 
			{
				Char = sData.charAt(i); 
				if (sValidChars.indexOf(Char) == -1) 
				{
					return null;
				}
				
				/* Only allowed one decimal place... */
				if ( Char == "." )
				{
					if ( bDecimal )
					{
						return null;
					}
					bDecimal = true;
				}
			}
			
			return 'numeric';
		},
		
		/*
		 * Function: -
		 * Purpose:  Check to see if a string is actually a formatted date
		 * Returns:  string:'date' or null
		 * Inputs:   string:sText - string to check
		 */
		function ( sData )
		{
			if ( ! isNaN(Date.parse(sData) ) )
			{
				return 'date';
			}
			return null;
		}
	];
	
	
	/*
	 * Variable: _oExternConfig
	 * Purpose:  Store information for DataTables to access globally about other instances
	 * Scope:    jQuery.fn.dataTableExt
	 */
	_oExt._oExternConfig = {
		/* int:iNextUnique - next unique number for an instance */
		"iNextUnique": 0
	};
	
	
	/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	 * DataTables prototype
	 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
	
	/*
	 * Function: dataTable
	 * Purpose:  DataTables information
	 * Returns:  -
	 * Inputs:   object:oInit - initalisation options for the table
	 */
	$.fn.dataTable = function( oInit )
	{
		/*
		 * Variable: _aoSettings
		 * Purpose:  Easy reference to data table settings
		 * Scope:    jQuery.dataTable
		 */
		var _aoSettings = $.fn.dataTableSettings;
		
		/*
		 * Function: classSettings
		 * Purpose:  Settings container function for all 'class' properties which are required
		 *   by dataTables
		 * Returns:  -
		 * Inputs:   -
		 */
		function classSettings ()
		{
			this.fnRecordsTotal = function ()
			{
				if ( this.oFeatures.bServerSide ) {
					return this._iRecordsTotal;
				} else {
					return this.aiDisplayMaster.length;
				}
			};
			
			this.fnRecordsDisplay = function ()
			{
				if ( this.oFeatures.bServerSide ) {
					return this._iRecordsDisplay;
				} else {
					return this.aiDisplay.length;
				}
			};
			
			this.fnDisplayEnd = function ()
			{
				if ( this.oFeatures.bServerSide ) {
					return this._iDisplayStart + this.aiDisplay.length;
				} else {
					return this._iDisplayEnd;
				}
			};
			
			/*
			 * Variable: sInstance
			 * Purpose:  Unique idendifier for each instance of the DataTables object
			 * Scope:    jQuery.dataTable.classSettings 
			 */
			this.sInstance = null;
			
			/*
			 * Variable: oFeatures
			 * Purpose:  Indicate the enablement of key dataTable features
			 * Scope:    jQuery.dataTable.classSettings 
			 */
			this.oFeatures = {
				"bPaginate": true,
				"bLengthChange": true,
				"bFilter": true,
				"bSort": true,
				"bInfo": true,
				"bAutoWidth": true,
				"bProcessing": false,
				"bSortClasses": true,
				"bStateSave": false,
				"bServerSide": false
			};
			
			/*
			 * Variable: anFeatures
			 * Purpose:  Array referencing the nodes which are used for the features
			 * Scope:    jQuery.dataTable.classSettings 
			 * Notes:    The parameters of this object match what is allowed by sDom - i.e.
			 *   'l' - Length changing
			 *   'f' - Filtering input
			 *   't' - The table!
			 *   'i' - Information
			 *   'p' - Pagination
			 *   'r' - pRocessing
			 */
			this.anFeatures = [];
			
			/*
			 * Variable: oLanguage
			 * Purpose:  Store the language strings used by dataTables
			 * Scope:    jQuery.dataTable.classSettings
			 * Notes:    The words in the format _VAR_ are variables which are dynamically replaced
			 *   by javascript
			 */
			this.oLanguage = {
				"sProcessing": "Processing...",
				"sLengthMenu": "Show _MENU_ entries",
				"sZeroRecords": "No matching records found",
				"sInfo": "Showing _START_ to _END_ of _TOTAL_ entries",
				"sInfoEmpty": "Showing 0 to 0 of 0 entries",
				"sInfoFiltered": "(filtered from _MAX_ total entries)",
				"sInfoPostFix": "",
				"sSearch": "",
				"sUrl": "",
				"oPaginate": {
					"sFirst":    "First",
					"sPrevious": "Previous",
					"sNext":     "Next",
					"sLast":     "Last"
				}
			};
			
			/*
			 * Variable: aoData
			 * Purpose:  Store data information
			 * Scope:    jQuery.dataTable.classSettings 
			 * Notes:    This is an array of objects with the following parameters:
			 *   int: _iId - internal id for tracking
			 *   array: _aData - internal data - used for sorting / filtering etc
			 *   node: nTr - display node
			 *   array node: _anHidden - hidden TD nodes
			 */
			this.aoData = [];
			
			/*
			 * Variable: aiDisplay
			 * Purpose:  Array of indexes which are in the current display (after filtering etc)
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.aiDisplay = [];
			
			/*
			 * Variable: aiDisplayMaster
			 * Purpose:  Array of indexes for display - no filtering
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.aiDisplayMaster = [];
							
			/*
			 * Variable: aoColumns
			 * Purpose:  Store information about each column that is in use
			 * Scope:    jQuery.dataTable.classSettings 
			 */
			this.aoColumns = [];
			
			/*
			 * Variable: iNextId
			 * Purpose:  Store the next unique id to be used for a new row
			 * Scope:    jQuery.dataTable.classSettings 
			 */
			this.iNextId = 0;
			
			/*
			 * Variable: asDataSearch
			 * Purpose:  Search data array for regular expression searching
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.asDataSearch = [];
			
			/*
			 * Variable: oPreviousSearch
			 * Purpose:  Store the previous search incase we want to force a re-search
			 *   or compare the old search to a new one
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.oPreviousSearch = {
				"sSearch": "",
				"bEscapeRegex": true
			};
			
			/*
			 * Variable: aoPreSearchCols
			 * Purpose:  Store the previous search for each column
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.aoPreSearchCols = [];
			
			/*
			 * Variable: aaSorting
			 * Purpose:  Sorting information
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.aaSorting = [ [0, 'asc'] ];
			
			/*
			 * Variable: aaSortingFixed
			 * Purpose:  Sorting information that is always applied
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.aaSortingFixed = null;
			
			/*
			 * Variable: asStripClasses
			 * Purpose:  Classes to use for the striping of a table
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.asStripClasses = [ 'odd', 'even' ];
			
			/*
			 * Variable: fnRowCallback
			 * Purpose:  Call this function every time a row is inserted (draw)
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.fnRowCallback = null;
			
			/*
			 * Variable: fnHeaderCallback
			 * Purpose:  Callback function for the header on each draw
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.fnHeaderCallback = null;
			
			/*
			 * Variable: fnFooterCallback
			 * Purpose:  Callback function for the footer on each draw
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.fnFooterCallback = null;
			
			/*
			 * Variable: fnDrawCallback
			 * Purpose:  Callback function for the whole table on each draw
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.fnDrawCallback = null;
			
			/*
			 * Variable: fnInitComplete
			 * Purpose:  Callback function for when the table has been initalised
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.fnInitComplete = null;
			
			/*
			 * Variable: sTableId
			 * Purpose:  Cache the table ID for quick access
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.sTableId = "";
			
			/*
			 * Variable: nTable
			 * Purpose:  Cache the table node for quick access
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.nTable = null;
			
			/*
			 * Variable: iDefaultSortIndex
			 * Purpose:  Sorting index which will be used by default
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.iDefaultSortIndex = 0;
			
			/*
			 * Variable: bInitialised
			 * Purpose:  Indicate if all required information has been read in
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.bInitialised = false;
			
			/*
			 * Variable: aoOpenRows
			 * Purpose:  Information about open rows
			 * Scope:    jQuery.dataTable.classSettings
			 * Notes:    Has the parameters 'nTr' and 'nParent'
			 */
			this.aoOpenRows = [];
			
			/*
			 * Variable: sDomPositioning
			 * Purpose:  Dictate the positioning that the created elements will take
			 * Scope:    jQuery.dataTable.classSettings
			 * Notes:    The following syntax is expected:
			 *   'l' - Length changing
			 *   'f' - Filtering input
			 *   't' - The table!
			 *   'i' - Information
			 *   'p' - Pagination
			 *   'r' - pRocessing
			 *   '<' and '>' - div elements
			 *   '<"class" and '>' - div with a class
			 *    Examples: '<"wrapper"flipt>', '<lf<t>ip>'
			 */
			this.sDomPositioning = 'lfrtip';
			
			/*
			 * Variable: sPaginationType
			 * Purpose:  Note which type of sorting should be used
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.sPaginationType = "two_button";
			
			/*
			 * Variable: iCookieDuration
			 * Purpose:  The cookie duration (for bStateSave) in seconds - default 2 hours
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.iCookieDuration = 60 * 60 * 2;
			
			/*
			 * Variable: sAjaxSource
			 * Purpose:  Source url for AJAX data for the table
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.sAjaxSource = null;

            this.oAjaxBaseData = {};
			
			/*
			 * Variable: bAjaxDataGet
			 * Purpose:  Note if draw should be blocked while getting data
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.bAjaxDataGet = true;
			
			/*
			 * Variable: fnServerData
			 * Purpose:  Function to get the server-side data - can be overruled by the developer
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.fnServerData = $.getJSON;

			/*
			 * Variable: sJSONDataElement
			 * Purpose:  Define the element in the json response to check for aaData
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.sJSONDataElement = 'payload';
			
			/*
			 * Variable: iServerDraw
			 * Purpose:  Counter and tracker for server-side processing draws
			 * Scope:    jQuery.dataTable.classSettings
			 */
			this.iServerDraw = 0;
			
			/*
			 * Variable: _iDisplayLength, _iDisplayStart, _iDisplayEnd
			 * Purpose:  Display length variables
			 * Scope:    jQuery.dataTable.classSettings
			 * Notes:    These variable must NOT be used externally to get the data length. Rather, use
			 *   the fnRecordsTotal() (etc) functions.
			 */
			this._iDisplayLength = 10;
			this._iDisplayStart = 0;
			this._iDisplayEnd = 10;
			
			/*
			 * Variable: _iRecordsTotal, _iRecordsDisplay
			 * Purpose:  Display length variables used for server side processing
			 * Scope:    jQuery.dataTable.classSettings
			 * Notes:    These variable must NOT be used externally to get the data length. Rather, use
			 *   the fnRecordsTotal() (etc) functions.
			 */
			this._iRecordsTotal = 0;
			this._iRecordsDisplay = 0;

            this._sPreviousFilter = null;
		}
		
		/*
		 * Variable: oApi
		 * Purpose:  Container for publicly exposed 'private' functions
		 * Scope:    jQuery.dataTable
		 */
		this.oApi = {};
		
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * API functions
		 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
		
		/*
		 * Function: fnDraw
		 * Purpose:  Redraw the table
		 * Returns:  -
		 * Inputs:   -
		 */
		this.fnDraw = function(data)
		{

            oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex]);
            if (data !== undefined && data !== null) {
                oSettings.oAjaxBaseData = data
            }

			_fnReDraw( oSettings  );
		};
		
		/*
		 * Function: fnFilter
		 * Purpose:  Filter the input based on data
		 * Returns:  -
		 * Inputs:   string:sInput - string to filter the table on
		 *           int:iColumn - optional - column to limit filtering to
		 *           bool:bEscapeRegex - optional - escape regex characters or not - default true
		 */
		this.fnFilter = function( sInput, iColumn, bEscapeRegex )
		{
            if (this._sPreviousFilter == sInput) {
                return false;
            }

            this._sPreviousFilter = sInput; 
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			
			if ( typeof bEscapeRegex == 'undefined' )
			{
				bEscapeRegex = true;
			}
			
			if ( typeof iColumn == "undefined" || iColumn === null )
			{
				/* Global filter */
				_fnFilterComplete( oSettings, {"sSearch":sInput, "bEscapeRegex": bEscapeRegex}, 1 );
			}
			else
			{
				/* Single column filter */
				oSettings.aoPreSearchCols[ iColumn ].sSearch = sInput;
				oSettings.aoPreSearchCols[ iColumn ].bEscapeRegex = bEscapeRegex;
				_fnFilterComplete( oSettings, oSettings.oPreviousSearch, 1 );
			}
		};
		
		/*
		 * Function: fnSettings
		 * Purpose:  Get the settings for a particular table for extern. manipulation
		 * Returns:  -
		 * Inputs:   -
		 */
		this.fnSettings = function( nNode  )
		{
			return _fnSettingsFromNode( this[_oExt.iApiIndex] );
		};
		
		/*
		 * Function: fnSort
		 * Purpose:  Sort the table by a particular row
		 * Returns:  -
		 * Inputs:   int:iCol - the data index to sort on. Note that this will
		 *   not match the 'display index' if you have hidden data entries
		 */
		this.fnSort = function( aaSort )
		{
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			oSettings.aaSorting = aaSort;
			_fnSort( oSettings );
		};
		
		/*
		 * Function: fnAddData
		 * Purpose:  Add new row(s) into the table
		 * Returns:  array int: array of indexes (aoData) which have been added (zero length on error)
		 * Inputs:   array:mData - the data to be added. The length must match
		 *               the original data from the DOM
		 *             or
		 *             array array:mData - 2D array of data to be added
		 *           bool:bRedraw - redraw the table or not - default true
		 * Notes:    Warning - the refilter here will cause the table to redraw
		 *             starting at zero
		 * Notes:    Thanks to Yekimov Denis for contributing the basis for this function!
		 */
		this.fnAddData = function( mData, bRedraw )
		{
			var aiReturn = [];
			var iTest;
			if ( typeof bRedraw == 'undefined' )
			{
				bRedraw = true;
			}
			
			/* Find settings from table node */
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			
			/* Check if we want to add multiple rows or not */
			if ( typeof mData[0] == "object" )
			{
				for ( var i=0 ; i<mData.length ; i++ )
				{
					iTest = _fnAddData( oSettings, mData[i] );
					if ( iTest == -1 )
					{
						return aiReturn;
					}
					aiReturn.push( iTest );
				}
			}
			else
			{
				iTest = _fnAddData( oSettings, mData );
				if ( iTest == -1 )
				{
					return aiReturn;
				}
				aiReturn.push( iTest );
			}
			
			oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
			
			/* Rebuild the search */
			_fnBuildSearchArray( oSettings, 1 );
			
			if ( bRedraw )
			{
				_fnReDraw( oSettings );
			}
			return aiReturn;
		};
		
		/*
		 * Function: fnDeleteRow
		 * Purpose:  Remove a row for the table
		 * Returns:  array:aReturn - the row that was deleted
		 * Inputs:   int:iIndex - index of aoData to be deleted
		 *           function:fnCallBack - callback function - default null
		 *           bool:bNullRow - remove the row information from aoData by setting the value to
		 *             null - default false
		 * Notes:    This function requires a little explanation - we don't actually delete the data
		 *   from aoData - rather we remove it's references from aiDisplayMastr and aiDisplay. This
		 *   in effect prevnts DataTables from drawing it (hence deleting it) - it could be restored
		 *   if you really wanted. The reason for this is that actually removing the aoData object
		 *   would mess up all the subsequent indexes in the display arrays (they could be ajusted - 
		 *   but this appears to do what is required).
		 */
		this.fnDeleteRow = function( iAODataIndex, fnCallBack, bNullRow )
		{
			/* Find settings from table node */
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			var i;
			
			/* Delete from the display master */
			for ( i=0 ; i<oSettings.aiDisplayMaster.length ; i++ )
			{
				if ( oSettings.aiDisplayMaster[i] == iAODataIndex )
				{
					oSettings.aiDisplayMaster.splice( i, 1 );
					break;
				}
			}
			
			/* Delete from the current display index */
			for ( i=0 ; i<oSettings.aiDisplay.length ; i++ )
			{
				if ( oSettings.aiDisplay[i] == iAODataIndex )
				{
					oSettings.aiDisplay.splice( i, 1 );
					break;
				}
			}
			
			/* Rebuild the search */
			_fnBuildSearchArray( oSettings, 1 );
			
			/* If there is a user callback function - call it */
			if ( typeof fnCallBack == "function" )
			{
				fnCallBack.call( this );
			}
			
			/* Check for an 'overflow' they case for dislaying the table */
			if ( oSettings._iDisplayStart >= oSettings.aiDisplay.length )
			{
				oSettings._iDisplayStart -= oSettings._iDisplayLength;
				if ( oSettings._iDisplayStart < 0 )
				{
					oSettings._iDisplayStart = 0;
				}
			}
			
			_fnCalculateEnd( oSettings );
			_fnDraw( oSettings );
			
			/* Return the data array from this row */
			var aData = oSettings.aoData[iAODataIndex]._aData.slice();
			
			if ( typeof bNullRow != "undefined" && bNullRow === true )
			{
				oSettings.aoData[iAODataIndex] = null;
			}
			
			return aData;
		};
		
		/*
		 * Function: fnClearTable
		 * Purpose:  Quickly and simply clear a table
		 * Returns:  -
		 * Inputs:   bool:bRedraw - redraw the table or not - default true
		 * Notes:    Thanks to Yekimov Denis for contributing the basis for this function!
		 */
		this.fnClearTable = function( bRedraw )
		{
			/* Find settings from table node */
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			_fnClearTable( oSettings );
			
			if ( typeof bRedraw == 'undefined' || bRedraw )
			{
				_fnDraw( oSettings );
			}
		};
		
		/*
		 * Function: fnOpen
		 * Purpose:  Open a display row (append a row after the row in question)
		 * Returns:  -
		 * Inputs:   node:nTr - the table row to 'open'
		 *           string:sHtml - the HTML to put into the row
		 *           string:sClass - class to give the new cell
		 */
		this.fnOpen = function( nTr, sHtml, sClass )
		{
			/* Find settings from table node */
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			
			/* the old open one if there is one */
			this.fnClose( nTr );
			
			
			var nNewRow = document.createElement("tr");
			var nNewCell = document.createElement("td");
			nNewRow.appendChild( nNewCell );
			nNewCell.className = sClass;
			nNewCell.colSpan = _fnVisbleColumns( oSettings );
			nNewCell.innerHTML = sHtml;
			
			$(nNewRow).insertAfter(nTr);
			
			/* No point in storing the row if using server-side processing since the nParent will be
			 * nuked on a re-draw anyway
			 */
			if ( !oSettings.oFeatures.bServerSide )
			{
				oSettings.aoOpenRows.push( {
					"nTr": nNewRow,
					"nParent": nTr
				} );
			}
		};
		
		/*
		 * Function: fnClose
		 * Purpose:  Close a display row
		 * Returns:  int: 0 (success) or 1 (failed)
		 * Inputs:   node:nTr - the table row to 'close'
		 */
		this.fnClose = function( nTr )
		{
			/* Find settings from table node */
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			
			for ( var i=0 ; i<oSettings.aoOpenRows.length ; i++ )
			{
				if ( oSettings.aoOpenRows[i].nParent == nTr )
				{
					var nTrParent = oSettings.aoOpenRows[i].nTr.parentNode;
					if ( nTrParent )
					{
						/* Remove it if it is currently on display */
						nTrParent.removeChild( oSettings.aoOpenRows[i].nTr );
					}
					oSettings.aoOpenRows.splice( i, 1 );
					return 0;
				}
			}
			return 1;
		};
		
		/*
		 * Function: fnGetData
		 * Purpose:  Return an array with the data which is used to make up the table
		 * Returns:  array array string: 2d data array ([row][column]) or array string: 1d data array
		 *           or
		 *           array string (if iRow specified)
		 * Inputs:   int:iRow - optional - if present then the array returned will be the data for
		 *             the row with the index 'iRow'
		 */
		this.fnGetData = function( iRow )
		{
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			
			if ( typeof iRow != 'undefined' )
			{
				return oSettings.aoData[iRow]._aData;
			}
			return _fnGetDataMaster( oSettings );
		};
		
		/*
		 * Function: fnGetNodes
		 * Purpose:  Return an array with the TR nodes used for drawing the table
		 * Returns:  array node: TR elements
		 *           or
		 *           node (if iRow specified)
		 * Inputs:   int:iRow - optional - if present then the array returned will be the node for
		 *             the row with the index 'iRow'
		 */
		this.fnGetNodes = function( iRow )
		{
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			
			if ( typeof iRow != 'undefined' )
			{
				return oSettings.aoData[iRow].nTr;
			}
			return _fnGetTrNodes( oSettings );
		};
		
		/*
		 * Function: fnGetPosition
		 * Purpose:  Get the array indexes of a particular cell from it's DOM element
		 * Returns:  int: - row index, or array[ int, int ]: - row index and column index
		 * Inputs:   node:nNode - this can either be a TR or a TD in the table, the return is
		 *             dependent on this input
		 */
		this.fnGetPosition = function( nNode )
		{
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			var i;
			
			if ( nNode.nodeName == "TR" )
			{
				for ( i=0 ; i<oSettings.aoData.length ; i++ )
				{
					if ( oSettings.aoData[i].nTr == nNode )
					{
						return i;
					}
				}
			}
			else if ( nNode.nodeName == "TD" )
			{
				for ( i=0 ; i<oSettings.aoData.length ; i++ )
				{
					var iCorrector = 0;
					for ( var j=0 ; j<oSettings.aoColumns.length ; j++ )
					{
						if ( oSettings.aoColumns[j].bVisible )
						{
							//$('>td', oSettings.aoData[i].nTr)[j-iCorrector] == nNode )
							if ( oSettings.aoData[i].nTr.getElementsByTagName('td')[j-iCorrector] == nNode )
							{
								return [ i, j-iCorrector, j ];
							}
						}
						else
						{
							iCorrector++;
						}
					}
				}
			}
			return null;
		};
		
		/*
		 * Function: fnUpdate
		 * Purpose:  Update a table cell or row
		 * Returns:  int: 0 okay, 1 error
		 * Inputs:   array string 'or' string:mData - data to update the cell/row with
		 *           int:iRow - the row (from aoData) to update
		 *           int:iColumn - the column to update
		 *           bool:bRedraw - redraw the table or not - default true
		 */
		this.fnUpdate = function( mData, iRow, iColumn, bRedraw )
		{
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			var iVisibleColumn;
			var sDisplay;
			if ( typeof bRedraw == 'undefined' )
			{
				bRedraw = true;
			}
			
			if ( typeof mData != 'object' )
			{
				sDisplay = mData;
				oSettings.aoData[iRow]._aData[iColumn] = sDisplay;
				
				if ( oSettings.aoColumns[iColumn].fnRender !== null )
				{
					sDisplay = oSettings.aoColumns[iColumn].fnRender( {
						"iDataRow": iRow,
						"iDataColumn": iColumn,
						"aData": oSettings.aoData[iRow]._aData
					} );
					
					if ( oSettings.aoColumns[iColumn].bUseRendered )
					{
						oSettings.aoData[iRow]._aData[iColumn] = sDisplay;
					}
				}
				
				iVisibleColumn = _fnColumnIndexToVisible( oSettings, iColumn );
				if ( iVisibleColumn !== null )
				{
					oSettings.aoData[iRow].nTr.getElementsByTagName('td')[iVisibleColumn].innerHTML = 
						sDisplay;
				}
			}
			else
			{
				if ( mData.length != oSettings.aoColumns.length )
				{
					alert( 'Warning: An array passed to fnUpdate must have the same number of columns as '+
						'the table in question - in this case '+oSettings.aoColumns.length );
					return 1;
				}
				
				for ( var i=0 ; i<mData.length ; i++ )
				{
					sDisplay = mData[i];
					oSettings.aoData[iRow]._aData[i] = sDisplay;
					
					if ( oSettings.aoColumns[i].fnRender !== null )
					{
						sDisplay = oSettings.aoColumns[i].fnRender( {
							"iDataRow": iRow,
							"iDataColumn": i,
							"aData": oSettings.aoData[iRow]._aData
						} );
						
						if ( oSettings.aoColumns[i].bUseRendered )
						{
							oSettings.aoData[iRow]._aData[i] = sDisplay;
						}
					}
					
					iVisibleColumn = _fnColumnIndexToVisible( oSettings, i );
					if ( iVisibleColumn !== null )
					{
						oSettings.aoData[iRow].nTr.getElementsByTagName('td')[iVisibleColumn].innerHTML = 
							sDisplay;
					}
				}
			}
			
			/* Update the search array */
			_fnBuildSearchArray( oSettings, 1 );
			
			/* Redraw the table */
			if ( bRedraw )
			{
				_fnReDraw( oSettings );
			}
			return 0;
		};
		
		
		/*
		 * Function: fnShowColoumn
		 * Purpose:  Show a particular column
		 * Returns:  -
		 * Inputs:   int:iCol - the column whose display should be changed
		 *           bool:bShow - show (true) or hide (false) the column
		 */
		this.fnSetColumnVis = function ( iCol, bShow )
		{
			var oSettings = _fnSettingsFromNode( this[_oExt.iApiIndex] );
			var i, iLen;
			var iColumns = oSettings.aoColumns.length;
			var nTd;
			
			/* No point in doing anything if we are requesting what is already true */
			if ( oSettings.aoColumns[iCol].bVisible == bShow )
			{
				return;
			}
			
			var nTrHead = $('thead tr', oSettings.nTable)[0];
			var nTrFoot = $('tfoot tr', oSettings.nTable)[0];
			var anTheadTh = [];
			var anTfootTh = [];
			for ( i=0 ; i<iColumns ; i++ )
			{
				anTheadTh.push( oSettings.aoColumns[i].nTh );
				anTfootTh.push( oSettings.aoColumns[i].nTf );
			}
			
			/* Show the column */
			if ( bShow )
			{
				var iInsert = 0;
				for ( i=0 ; i<iCol ; i++ )
				{
					if ( oSettings.aoColumns[i].bVisible )
					{
						iInsert++;
					}
				}
				
				/* Need to decide if we should use appendChild or insertBefore */
				if ( iInsert >= _fnVisbleColumns( oSettings ) )
				{
					nTrHead.appendChild( anTheadTh[iCol] );
					if ( nTrFoot )
					{
						nTrFoot.appendChild( anTfootTh[iCol] );
					}
					
					for ( i=0, iLen=oSettings.aoData.length ; i<iLen ; i++ )
					{
						nTd = oSettings.aoData[i]._anHidden[iCol];
						oSettings.aoData[i].nTr.appendChild( nTd );
					}
				}
				else
				{
					/* Which coloumn should we be inserting before? */
					var iBefore;
					for ( i=iCol ; i<iColumns ; i++ )
					{
						iBefore = _fnColumnIndexToVisible( oSettings, i );
						if ( iBefore !== null )
						{
							break;
						}
					}
					
					nTrHead.insertBefore( anTheadTh[iCol], nTrHead.getElementsByTagName('th')[iBefore] );
					if ( nTrFoot )
					{
						nTrFoot.insertBefore( anTfootTh[iCol], nTrFoot.getElementsByTagName('th')[iBefore] );
					}
					
					for ( i=0, iLen=oSettings.aoData.length ; i<iLen ; i++ )
					{
						nTd = oSettings.aoData[i]._anHidden[iCol];
						oSettings.aoData[i].nTr.insertBefore( nTd, oSettings.aoData[i].nTr.getElementsByTagName('td')[iBefore] );
					}
				}
				
				oSettings.aoColumns[iCol].bVisible = true;
			}
			else
			{
				/* Remove a column from display */
				nTrHead.removeChild( anTheadTh[iCol] );
				if ( nTrFoot )
				{
					nTrFoot.removeChild( anTfootTh[iCol] );
				}
				
				var iVisCol = _fnColumnIndexToVisible(oSettings, iCol);
				for ( i=0, iLen=oSettings.aoData.length ; i<iLen ; i++ )
				{
					nTd = oSettings.aoData[i].nTr.getElementsByTagName('td')[ iVisCol ];
					oSettings.aoData[i]._anHidden[iCol] = nTd;
					nTd.parentNode.removeChild( nTd );
				}
				
				oSettings.aoColumns[iCol].bVisible = false;
			}
			
			/* Since there is no redraw done here, we need to save the state manually */
			_fnSaveState( oSettings );
		};
		
		
		/*
		 * Plugin API functions
		 * 
		 * This call will add the functions which are defined in _oExt.oApi to the
		 * DataTables object, providing a rather nice way to allow plug-in API functions. Note that
		 * this is done here, so that API function can actually override the built in API functions if
		 * required for a particular purpose.
		 */
		
		/*
		 * Function: _fnExternApiFunc
		 * Purpose:  Create a wrapper function for exporting an internal func to an external API func
		 * Returns:  function: - wrapped function
		 * Inputs:   string:sFunc - API function name
		 */
		function _fnExternApiFunc (sFunc)
		{
			return function() {
					var aArgs = [_fnSettingsFromNode(this[_oExt.iApiIndex])].concat( 
						Array.prototype.slice.call(arguments) );
					return _oExt.oApi[sFunc].apply( this, aArgs );
				};
		}
		
		for ( var sFunc in _oExt.oApi )
		{
			if ( sFunc )
			{
				/*
				 * Function: anon
				 * Purpose:  Wrap the plug-in API functions in order to provide the settings as 1st arg 
				 *   and execute in this scope
				 * Returns:  -
				 * Inputs:   -
				 */
				this[sFunc] = _fnExternApiFunc(sFunc);
			}
		}
		
		
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Local functions
		 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Initalisation
		 */
		
		/*
		 * Function: _fnInitalise
		 * Purpose:  Draw the table for the first time, adding all required features
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnInitalise ( oSettings )
		{
			/* Ensure that the table data is fully initialised */
			if ( oSettings.bInitialised === false )
			{
				setTimeout( function(){ _fnInitalise( oSettings ); }, 200 );
				return;
			}
			
			/* Show the display HTML options */
			_fnAddOptionsHtml( oSettings );
			
			/* Draw the headers for the table */
			_fnDrawHead( oSettings );
			
			/* If there is default sorting required - let's do it. The sort function
			 * will do the drawing for us. Otherwise we draw the table
			 */
			if ( oSettings.oFeatures.bSort )
			{
				_fnSort( oSettings, false );
				/*
				 * Add the sorting classes to the header and the body (if needed).
				 * Reason for doing it here after the first draw is to stop classes being applied to the
				 * 'static' table.
				 */
				_fnSortingClasses( oSettings );
			}
			else
			{
				oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
				_fnCalculateEnd( oSettings );
				_fnDraw( oSettings );
			}
			
			/* if there is an ajax source */
			if ( oSettings.sAjaxSource !== null && !oSettings.oFeatures.bServerSide )
			{
				_fnProcessingDisplay( oSettings, true );

				$.ajax({
                    url : oSettings.sAjaxSource, 
                    dataType: 'json',
                    timeout : 10000,
                    data: null,
                    success: function (json) {
                        /* Got the data - add it to the table */
                        var aoJSON = json[oSettings.sJSONDataElement];

                        for ( var i=0 ; i<aoJSON.aaData.length ; i++ )
                        {
                            _fnAddData( oSettings, aoJSON.aaData[i] );
                        }
                        
                        if ( oSettings.oFeatures.bSort )
                        {
                            _fnSort( oSettings );
                        }
                        else
                        {
                            oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
                            _fnCalculateEnd( oSettings );
                            _fnDraw( oSettings );
                        }
                        _fnProcessingDisplay( oSettings, false );
                        
                        /* Run the init callback if there is one */
                        if ( typeof oSettings.fnInitComplete == 'function' )
                        {
                            oSettings.fnInitComplete( oSettings, aoJSON );
                        }

                        return;
                    }
                });
            }
			
			/* Run the init callback if there is one */
			if ( typeof oSettings.fnInitComplete == 'function' )
			{
				oSettings.fnInitComplete( oSettings );
			}
		}
		
		/*
		 * Function: _fnLanguageProcess
		 * Purpose:  Copy language variables from remote object to a local one
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           object:oLanguage - Language information
		 *           bool:bInit - init once complete
		 */
		function _fnLanguageProcess( oSettings, oLanguage, bInit )
		{
			_fnMap( oSettings.oLanguage, oLanguage, 'sProcessing' );
			_fnMap( oSettings.oLanguage, oLanguage, 'sLengthMenu' );
			_fnMap( oSettings.oLanguage, oLanguage, 'sZeroRecords' );
			_fnMap( oSettings.oLanguage, oLanguage, 'sInfo' );
			_fnMap( oSettings.oLanguage, oLanguage, 'sInfoEmpty' );
			_fnMap( oSettings.oLanguage, oLanguage, 'sInfoFiltered' );
			_fnMap( oSettings.oLanguage, oLanguage, 'sInfoPostFix' );
			_fnMap( oSettings.oLanguage, oLanguage, 'sSearch' );
			
			if ( typeof oLanguage.oPaginate != 'undefined' )
			{
				_fnMap( oSettings.oLanguage.oPaginate, oLanguage.oPaginate, 'sFirst' );
				_fnMap( oSettings.oLanguage.oPaginate, oLanguage.oPaginate, 'sPrevious' );
				_fnMap( oSettings.oLanguage.oPaginate, oLanguage.oPaginate, 'sNext' );
				_fnMap( oSettings.oLanguage.oPaginate, oLanguage.oPaginate, 'sLast' );
			}
			
			if ( bInit )
			{
				_fnInitalise( oSettings );
			}
		}
		
		/*
		 * Function: _fnAddColumn
		 * Purpose:  Add a column to the list used for the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           object:oOptions - object with sType, bVisible and bSearchable
		 *           node:nTh - the th element for this column
		 * Notes:    All options in enter column can be over-ridden by the user
		 *   initialisation of dataTables
		 */
		function _fnAddColumn( oSettings, oOptions, nTh )
		{
			oSettings.aoColumns[ oSettings.aoColumns.length++ ] = {
				"sType": null,
				"_bAutoType": true,
				"bVisible": true,
				"bSearchable": true,
				"bSortable": true,
				"sTitle": nTh ? nTh.innerHTML : '',
				"sName": '',
				"sWidth": null,
				"sClass": null,
				"fnRender": null,
				"bUseRendered": true,
				"iDataSort": oSettings.aoColumns.length-1,
				"nTh": nTh ? nTh : document.createElement('th'),
				"nTf": null
			};
			
			/* User specified column options */
			var iLength = oSettings.aoColumns.length-1;
			if ( typeof oOptions != 'undefined' && oOptions !== null )
			{
				var oCol = oSettings.aoColumns[ iLength ];
				
				if ( typeof oOptions.sType != 'undefined' )
				{
					oCol.sType = oOptions.sType;
					oCol._bAutoType = false;
				}
				
				_fnMap( oCol, oOptions, "bVisible" );
				_fnMap( oCol, oOptions, "bSearchable" );
				_fnMap( oCol, oOptions, "bSortable" );
				_fnMap( oCol, oOptions, "sTitle" );
				_fnMap( oCol, oOptions, "sName" );
				_fnMap( oCol, oOptions, "sWidth" );
				_fnMap( oCol, oOptions, "sClass" );
				_fnMap( oCol, oOptions, "fnRender" );
				_fnMap( oCol, oOptions, "bUseRendered" );
				_fnMap( oCol, oOptions, "iDataSort" );
			}
			
			/* Add a column specific filter */
			if ( typeof oSettings.aoPreSearchCols[ iLength ] == 'undefined' ||
			     oSettings.aoPreSearchCols[ iLength ] === null )
			{
				oSettings.aoPreSearchCols[ iLength ] = {
					"sSearch": "",
					"bEscapeRegex": true
				};
			}
			else if ( typeof oSettings.aoPreSearchCols[ iLength ].bEscapeRegex == 'undefined' )
			{
				/* Don't require that the user must specify bEscapeRegex */
				oSettings.aoPreSearchCols[ iLength ].bEscapeRegex = true;
			}
		}
		
		/*
		 * Function: _fnAddData
		 * Purpose:  Add a data array to the table, creating DOM node etc
		 * Returns:  int: - >=0 if successful (index of new aoData entry), -1 if failed
		 * Inputs:   object:oSettings - dataTables settings object
		 *           array:aData - data array to be added
		 */
		function _fnAddData ( oSettings, aData )
		{
            
            // I send back an object for the data, generated from a PHP assoc
            // array going through json_encode
            // looks like we need an array for this to work
            if( typeof aData == "object") {

                var d = [];
                for (k in aData) {
                    d.push(aData[k]); 
                }

                aData = d;
            }

			/* Sanity check the length of the new array */
			if ( aData.length != oSettings.aoColumns.length )
			{
				console.log( "Warning - added data does not match known column length" );
				return -1;
			}
			
			/* Create the object for storing information about this new row */
			var iThisIndex = oSettings.aoData.length;
			oSettings.aoData.push( {
				"_iId": oSettings.iNextId++,
				"_aData": aData.slice(),
				"nTr": document.createElement('tr'),
				"_anHidden": []
			} );
			
			/* Create the cells */
			var nTd;
			for ( var i=0 ; i<aData.length ; i++ )
			{
				nTd = document.createElement('td');
				
				if ( typeof oSettings.aoColumns[i].fnRender == 'function' )
				{
					var sRendered = oSettings.aoColumns[i].fnRender( {
							"iDataRow": iThisIndex,
							"iDataColumn": i,
							"aData": aData
						} );
					nTd.innerHTML = sRendered;
					if ( oSettings.aoColumns[i].bUseRendered )
					{
						/* Use the rendered data for filtering/sorting */
						oSettings.aoData[iThisIndex]._aData[i] = sRendered;
					}
				}
				else
				{
					nTd.innerHTML = aData[i];
				}
				
				if ( oSettings.aoColumns[i].sClass !== null )
				{
					nTd.className = oSettings.aoColumns[i].sClass;
				}
				
				/* See if we should auto-detect the column type */
				if ( oSettings.aoColumns[i]._bAutoType && oSettings.aoColumns[i].sType != 'string' )
				{
					/* Attempt to auto detect the type - same as _fnGatherData() */
					if ( oSettings.aoColumns[i].sType === null )
					{
						oSettings.aoColumns[i].sType = _fnDetectType( aData[i] );
					}
					else if ( oSettings.aoColumns[i].sType == "date" || 
					          oSettings.aoColumns[i].sType == "numeric" )
					{
						oSettings.aoColumns[i].sType = _fnDetectType( aData[i] );
					}
				}
					
				if ( oSettings.aoColumns[i].bVisible )
				{
					oSettings.aoData[iThisIndex].nTr.appendChild( nTd );
				}
				else
				{
					oSettings.aoData[iThisIndex]._anHidden[i] = nTd;
				}
			}
			
			/* Add to the display array */
			oSettings.aiDisplayMaster.push( iThisIndex );
			return iThisIndex;
		}
		
		/*
		 * Function: _fnGatherData
		 * Purpose:  Read in the data from the target table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnGatherData( oSettings )
		{
			var iLoop;
			var i, j;
			
			/*
			 * Process by row first
			 * Add the data object for the whole table - storing the tr node. Note - no point in getting
			 * DOM based data if we are going to go and replace it with Ajax source data.
			 */
			if ( oSettings.sAjaxSource === null )
			{
				$('tbody:eq(0)>tr', oSettings.nTable).each( function() {
					var iThisIndex = oSettings.aoData.length;
					oSettings.aoData.push( {
						"_iId": oSettings.iNextId++,
						"_aData": [],
						"nTr": this,
						"_anHidden": []
					} );
					
					oSettings.aiDisplayMaster.push( iThisIndex );
					
					/* Add the data for this column */
					var aLocalData = oSettings.aoData[iThisIndex]._aData;
					$('td', this).each( function( i ) {
						aLocalData[i] = this.innerHTML;
					} );
				} );
			}
			
			/*
			 * Now process by column
			 */
			var iCorrector = 0;
			for ( i=0 ; i<oSettings.aoColumns.length ; i++ )
			{
				/* Get the title of the column - unless there is a user set one */
				if ( oSettings.aoColumns[i].sTitle === null )
				{
					oSettings.aoColumns[i].sTitle = oSettings.aoColumns[i].nTh.innerHTML;
				}
				
				var bAutoType = oSettings.aoColumns[i]._bAutoType;
				var bRender = typeof oSettings.aoColumns[i].fnRender == 'function';
				var bClass = oSettings.aoColumns[i].sClass !== null;
				var bVisible = oSettings.aoColumns[i].bVisible;
				
				/* A single loop to rule them all (and be more efficient) */
				if ( bAutoType || bRender || bClass || !bVisible )
				{
					iLoop = oSettings.aoData.length;
					for ( j=0 ; j<iLoop ; j++ )
					{
						var nCellNode = oSettings.aoData[j].nTr.getElementsByTagName('td')[ i-iCorrector ];
						
						if ( bAutoType )
						{
							if ( oSettings.aoColumns[i].sType === null )
							{
								oSettings.aoColumns[i].sType = _fnDetectType( oSettings.aoData[j]._aData[i] );
							}
							else if ( oSettings.aoColumns[i].sType == "date" || 
							          oSettings.aoColumns[i].sType == "numeric" )
							{
								/* If type is date or numeric - ensure that all collected data
								 * in the column is of the same type
								 */
								oSettings.aoColumns[i].sType = _fnDetectType( oSettings.aoData[j]._aData[i] );
							}
							/* The else would be 'type = string' we don't want to do anything
							 * if that is the case
							 */
						}
						
						if ( bRender )
						{
							var sRendered = oSettings.aoColumns[i].fnRender( {
									"iDataRow": j,
									"iDataColumn": i,
									"aData": oSettings.aoData[j]._aData
								} );
							nCellNode.innerHTML = sRendered;
							if ( oSettings.aoColumns[i].bUseRendered )
							{
								/* Use the rendered data for filtering/sorting */
								oSettings.aoData[j]._aData[i] = sRendered;
							}
						}
						
						if ( bClass )
						{
							nCellNode.className += ' '+oSettings.aoColumns[i].sClass;
						}
						
						if ( !bVisible )
						{
							oSettings.aoData[j]._anHidden[i] = nCellNode;
							nCellNode.parentNode.removeChild( nCellNode );
						}
					}
					
					/* Keep an index corrector for the next loop */
					if ( !bVisible )
					{
						iCorrector++;
					}
				}
			}	
		}
		
		
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Drawing functions
		 */
		
		/*
		 * Function: _fnDrawHead
		 * Purpose:  Create the HTML header for the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnDrawHead( oSettings )
		{
			var i, nTh, iLen;
			var iThs = oSettings.nTable.getElementsByTagName('thead')[0].getElementsByTagName('th').length;
			var iCorrector = 0;
			
			/* If there is a header in place - then use it - otherwise it's going to get nuked... */
			if ( iThs !== 0 )
			{
				/* We've got a thead from the DOM, so remove hidden columns and apply width to vis cols */
				for ( i=0, iLen=oSettings.aoColumns.length ; i<iLen ; i++ )
				{
					//oSettings.aoColumns[i].nTh = nThs[i];
					nTh = oSettings.aoColumns[i].nTh;
					
					if ( oSettings.aoColumns[i].bVisible )
					{
						/* Set width */
						if ( oSettings.aoColumns[i].sWidth !== null )
						{
							nTh.style.width = oSettings.aoColumns[i].sWidth;
						}
						
						/* Set the title of the column if it is user defined (not what was auto detected) */
						if ( oSettings.aoColumns[i].sTitle != nTh.innerHTML )
						{
							nTh.innerHTML = oSettings.aoColumns[i].sTitle;
						}
					}
					else
					{
						nTh.parentNode.removeChild( nTh );
						iCorrector++;
					}
				}
			}
			else
			{
				/* We don't have a header in the DOM - so we are going to have to create one */
				var nTr = document.createElement( "tr" );
				
				for ( i=0, iLen=oSettings.aoColumns.length ; i<iLen ; i++ )
				{
					if ( oSettings.aoColumns[i].bVisible )
					{
						nTh = oSettings.aoColumns[i].nTh;
						
						if ( oSettings.aoColumns[i].sClass !== null )
						{
							nTh.className = oSettings.aoColumns[i].sClass;
						}
						
						if ( oSettings.aoColumns[i].sWidth !== null )
						{
							nTh.style.width = oSettings.aoColumns[i].sWidth;
						}
						
						nTh.innerHTML = oSettings.aoColumns[i].sTitle;
						nTr.appendChild( nTh );
					}
				}
				$('thead', oSettings.nTable).html( '' )[0].appendChild( nTr );
			}
			
			
			/* Add sort listener */
			if ( oSettings.oFeatures.bSort )
			{
				for ( i=0 ; i<oSettings.aoColumns.length ; i++ )
				{
					if ( oSettings.aoColumns[i].bSortable === false )
					{
						continue;
					}
					
					$(oSettings.aoColumns[i].nTh).click( function (e) {
						var iDataIndex;
						/* Find which column we are sorting on - can't use index() due to colspan etc */
						for ( var i=0 ; i<oSettings.aoColumns.length ; i++ )
						{
							if ( oSettings.aoColumns[i].nTh == this )
							{
								iDataIndex = i;
								break;
							}
						}
						
						/* If the column is not sortable - don't to anything */
						if ( oSettings.aoColumns[iDataIndex].bSortable === false )
						{
							return;
						}
						
						/*
						 * This is a little bit odd I admit... I declare a temporary function inside the scope of
						 * _fnDrawHead and the click handler in order that the code presented here can be used 
						 * twice - once for when bProcessing is enabled, and another time for when it is 
						 * disabled, as we need to perform slightly different actions.
						 *   Basically the issue here is that the Javascript engine in modern browsers don't 
						 * appear to allow the rendering engine to update the display while it is still excuting
						 * it's thread (well - it does but only after long intervals). This means that the 
						 * 'processing' display doesn't appear for a table sort. To break the js thread up a bit
						 * I force an execution break by using setTimeout - but this breaks the expected 
						 * thread continuation for the end-developer's point of view (their code would execute
						 * too early), so we on;y do it when we absolutely have to.
						 */
						var fnInnerSorting = function () {
							if ( e.shiftKey )
							{
								/* If the shift key is pressed then we are multipe column sorting */
								var bFound = false;
								for ( var i=0 ; i<oSettings.aaSorting.length ; i++ )
								{
									if ( oSettings.aaSorting[i][0] == iDataIndex )
									{
										if ( oSettings.aaSorting[i][1] == "asc" )
										{
											oSettings.aaSorting[i][1] = "desc";
										}
										else
										{
											oSettings.aaSorting.splice( i, 1 );
										}
										bFound = true;
										break;
									}
								}
								
								if ( bFound === false )
								{
									oSettings.aaSorting.push( [ iDataIndex, "asc" ] );
								}
							}
							else
							{
								/* If no shift key then single column sort */
								if ( oSettings.aaSorting.length == 1 && oSettings.aaSorting[0][0] == iDataIndex )
								{
									oSettings.aaSorting[0][1] = oSettings.aaSorting[0][1]=="asc" ? "desc" : "asc";
								}
								else
								{
									oSettings.aaSorting.splice( 0, oSettings.aaSorting.length );
									oSettings.aaSorting.push( [ iDataIndex, "asc" ] );
								}
							}
							
							/* Run the sort */
							_fnSort( oSettings );
						}; /* /fnInnerSorting */
						
						if ( !oSettings.oFeatures.bProcessing )
						{
							fnInnerSorting();
						}
						else
						{
							_fnProcessingDisplay( oSettings, true );
							setTimeout( function() {
								fnInnerSorting();
								if ( !oSettings.oFeatures.bServerSide )
								{
									_fnProcessingDisplay( oSettings, false );
								}
							}, 0 );
						}
					} ); /* /click */
				} /* For each column */
				
				/* Take the brutal approach to cancelling text selection due to the shift key */
				$('thead th', oSettings.nTable).mousedown( function (e) {
					if ( e.shiftKey )
					{
						this.onselectstart = function() { return false; };
						return false;
					}
				} );
			} /* /if feature sort */
			
			/* Set an absolute width for the table such that pagination doesn't
			 * cause the table to resize
			 */
			if ( oSettings.oFeatures.bAutoWidth )
			{
				oSettings.nTable.style.width = oSettings.nTable.offsetWidth+"px";
			}
			
			/* Cache the footer elements */
			var nTfoot = oSettings.nTable.getElementsByTagName('tfoot');
			if ( nTfoot.length !== 0 )
			{
				iCorrector = 0;
				var nTfs = nTfoot[0].getElementsByTagName('th');
				for ( i=0, iLen=nTfs.length ; i<iLen ; i++ )
				{
					oSettings.aoColumns[i].nTf = nTfs[i-iCorrector];
					if ( !oSettings.aoColumns[i].bVisible )
					{
						nTfs[i-iCorrector].parentNode.removeChild( nTfs[i-iCorrector] );
						iCorrector++;
					}
				}
			}
		}
		
		/*
		 * Function: _fnDraw
		 * Purpose:  Insert the required TR nodes into the table for display
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnDraw( oSettings )
		{
			var i;
			var anRows = [];
			var iRowCount = 0;
			var bRowError = false;
			var iStrips = oSettings.asStripClasses.length;
			var iOpenRows = oSettings.aoOpenRows.length;
			
			/* If we are dealing with Ajax - do it here */
			if ( oSettings.oFeatures.bServerSide && 
			     !_fnAjaxUpdate( oSettings ) )
			{
				return;
			}
			
			if ( oSettings.aiDisplay.length !== 0 )
			{
				var iStart = oSettings._iDisplayStart;
				var iEnd = oSettings._iDisplayEnd;
				
				if ( oSettings.oFeatures.bServerSide )
				{
					iStart = 0;
					iEnd = oSettings.aoData.length;
				}
				
				for ( var j=iStart ; j<iEnd ; j++ )
				{
					var nRow = oSettings.aoData[ oSettings.aiDisplay[j] ].nTr;
					
					/* Remove any old stripping classes and then add the new one */
					if ( iStrips !== 0 )
					{
						$(nRow).removeClass( oSettings.asStripClasses.join(' ') );
						$(nRow).addClass( oSettings.asStripClasses[ iRowCount % iStrips ] );
					}
					
					/* Custom row callback function - might want to manipule the row */
					if ( typeof oSettings.fnRowCallback == "function" )
					{
						nRow = oSettings.fnRowCallback( nRow, 
							oSettings.aoData[ oSettings.aiDisplay[j] ]._aData, iRowCount, j );
						if ( !nRow && !bRowError )
						{
							alert( "Error: A node was not returned by fnRowCallback" );
							bRowError = true;
						}
					}
					
					anRows.push( nRow );
					iRowCount++;
					
					/* If there is an open row - and it is attached to this parent - attach it on redraw */
					if ( iOpenRows !== 0 )
					{
						for ( var k=0 ; k<iOpenRows ; k++ )
						{
							if ( nRow == oSettings.aoOpenRows[k].nParent )
							{
								anRows.push( oSettings.aoOpenRows[k].nTr );
							}
						}
					}
				}
			}
			else
			{
				/* Table is empty - create a row with an empty message in it */
				anRows[ 0 ] = document.createElement( 'tr' );
				
				if ( typeof oSettings.asStripClasses[0] != 'undefined' )
				{
					anRows[ 0 ].className = oSettings.asStripClasses[0];
				}
				
				var nTd = document.createElement( 'td' );
				nTd.setAttribute( 'valign', "top" );
				nTd.colSpan = oSettings.aoColumns.length;
				nTd.className = 'dataTables_empty';
				nTd.innerHTML = oSettings.oLanguage.sZeroRecords;
				
				anRows[ iRowCount ].appendChild( nTd );
			}
			
			/* Callback the header and footer custom funcation if there is one */
			if ( typeof oSettings.fnHeaderCallback == 'function' )
			{
				oSettings.fnHeaderCallback( $('thead tr', oSettings.nTable)[0], 
					_fnGetDataMaster( oSettings ), oSettings._iDisplayStart, oSettings.fnDisplayEnd(),
					oSettings.aiDisplay );
			}
			
			if ( typeof oSettings.fnFooterCallback == 'function' )
			{
				oSettings.fnFooterCallback( $('tfoot tr', oSettings.nTable)[0], 
					_fnGetDataMaster( oSettings ), oSettings._iDisplayStart, oSettings.fnDisplayEnd(),
					oSettings.aiDisplay );
			}
			
			/* 
			 * Need to remove any old row from the display - note we can't just empty the tbody using
			 * .html('') since this will unbind the jQuery event handlers (even although the node still
			 * exists!) - note the initially odd ':eq(0)>tr' expression. This basically ensures that we
			 * only get tr elements of the tbody that the data table has been initialised on. If there
			 * are nested tables then we don't want to remove those elements.
			 */
			var nTrs = $('tbody:eq(0)>tr', oSettings.nTable);
			for ( i=0 ; i<nTrs.length ; i++ )
			{
				nTrs[i].parentNode.removeChild( nTrs[i] );
			}
			
			/* Put the draw table into the dom */
			var nBody = $('tbody:eq(0)', oSettings.nTable);
			if ( nBody[0] )
			{
				for ( i=0 ; i<anRows.length ; i++ )
				{
					nBody[0].appendChild( anRows[i] );
				}
			}
			
			/* Update the pagination display buttons */
			if ( oSettings.oFeatures.bPaginate )
			{
				_oExt.oPagination[ oSettings.sPaginationType ].fnUpdate( oSettings, function( oSettings ) {
					_fnCalculateEnd( oSettings );
					_fnDraw( oSettings );
				} );
			}
			
			/* Show information about the table */
			if ( oSettings.oFeatures.bInfo && oSettings.anFeatures.i )
			{
				/* Update the information */
				if ( oSettings.fnRecordsDisplay() === 0 && 
					   oSettings.fnRecordsDisplay() == oSettings.fnRecordsTotal() )
				{
					oSettings.anFeatures.i.innerHTML = 
						oSettings.oLanguage.sInfoEmpty+ oSettings.oLanguage.sInfoPostFix;
				}
				else if ( oSettings.fnRecordsDisplay() === 0 )
				{
					oSettings.anFeatures.i.innerHTML = oSettings.oLanguage.sInfoEmpty +' '+ 
						oSettings.oLanguage.sInfoFiltered.replace('_MAX_', 
							oSettings.fnRecordsTotal())+ oSettings.oLanguage.sInfoPostFix;
				}
				else if ( oSettings.fnRecordsDisplay() == oSettings.fnRecordsTotal() )
				{
					oSettings.anFeatures.i.innerHTML = 
						oSettings.oLanguage.sInfo.
							replace('_START_',oSettings._iDisplayStart+1).
							replace('_END_',oSettings.fnDisplayEnd()).
							replace('_TOTAL_',oSettings.fnRecordsDisplay())+ 
						oSettings.oLanguage.sInfoPostFix;
				}
				else
				{
					oSettings.anFeatures.i.innerHTML = 
						oSettings.oLanguage.sInfo.
							replace('_START_',oSettings._iDisplayStart+1).
							replace('_END_',oSettings.fnDisplayEnd()).
							replace('_TOTAL_',oSettings.fnRecordsDisplay()) +' '+ 
						oSettings.oLanguage.sInfoFiltered.replace('_MAX_', oSettings.fnRecordsTotal())+ 
						oSettings.oLanguage.sInfoPostFix;
				}
			}
			
			/* Alter the sorting classes to take account of the changes */
			if ( oSettings.oFeatures.bServerSide && oSettings.oFeatures.bSort )
			{
				_fnSortingClasses( oSettings );
			}
			
			/* Save the table state on each draw */
			_fnSaveState( oSettings );
			
			/* Drawing is finished - call the callback if there is one */
			if ( typeof oSettings.fnDrawCallback == 'function' )
			{
				oSettings.fnDrawCallback( oSettings );
			}
		}
		
		/*
		 * Function: _fnReDraw
		 * Purpose:  Redraw the table - taking account of the various features which are enabled
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnReDraw( oSettings )
		{
			if ( oSettings.oFeatures.bSort )
			{
				/* Sorting will refilter and draw for us */
				_fnSort( oSettings, oSettings.oPreviousSearch );
			}
			else if ( oSettings.oFeatures.bFilter )
			{
				/* Filtering will redraw for us */
				_fnFilterComplete( oSettings, oSettings.oPreviousSearch );
			}
			else
			{
				_fnCalculateEnd( oSettings );
				_fnDraw( oSettings );
			}
		}
		
		/*
		 * Function: _fnAjaxUpdate
		 * Purpose:  Update the table using an Ajax call
		 * Returns:  bool: block the table drawing or not
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnAjaxUpdate( oSettings )
		{
            
			if ( oSettings.bAjaxDataGet )
			{
				_fnProcessingDisplay( oSettings, true );
				var iColumns = oSettings.aoColumns.length;
				var aoData = [];
				var i;

                /* Adding AjaxBaseData to the url 
                 *  Let's us provide an object of base data, say a feed id into
                 *  all requests made by this datagrid. 
                 *
                 */
                for (key in oSettings.oAjaxBaseData) {
                    aoData.push( { "name": key,          "value": oSettings.oAjaxBaseData[key] } );
                }
                
				/* Paging and general */
				oSettings.iServerDraw++;
				aoData.push( { "name": "sEcho",          "value": oSettings.iServerDraw } );
				aoData.push( { "name": "iColumns",       "value": iColumns } );
				aoData.push( { "name": "sColumns",       "value": _fnColumnOrdering(oSettings) } );
				aoData.push( { "name": "iDisplayStart",  "value": oSettings._iDisplayStart } );
				aoData.push( { "name": "iDisplayLength", "value": oSettings.oFeatures.bPaginate !== false ?
					oSettings._iDisplayLength : -1 } );
				
				/* Filtering */
				if ( oSettings.oFeatures.bFilter !== false )
				{
					aoData.push( { "name": "sSearch",        "value": oSettings.oPreviousSearch.sSearch } );
					aoData.push( { "name": "bEscapeRegex",   "value": oSettings.oPreviousSearch.bEscapeRegex } );
					for ( i=0 ; i<iColumns ; i++ )
					{
						aoData.push( { "name": "sSearch_"+i,      "value": oSettings.aoPreSearchCols[i].sSearch } );
						aoData.push( { "name": "bEscapeRegex_"+i, "value": oSettings.aoPreSearchCols[i].bEscapeRegex } );
					}
				}
				
				/* Sorting */
				if ( oSettings.oFeatures.bSort !== false )
				{
					var iFixed = oSettings.aaSortingFixed !== null ? oSettings.aaSortingFixed.length : 0;
					var iUser = oSettings.aaSorting.length;
					aoData.push( { "name": "iSortingCols",   "value": iFixed+iUser } );
					for ( i=0 ; i<iFixed ; i++ )
					{
						aoData.push( { "name": "iSortCol_"+i,  "value": oSettings.aaSortingFixed[i][0] } );
						aoData.push( { "name": "iSortDir_"+i,  "value": oSettings.aaSortingFixed[i][1] } );
					}
					
					for ( i=0 ; i<iUser ; i++ )
					{
						aoData.push( { "name": "iSortCol_"+(i+iFixed),  "value": oSettings.aaSorting[i][0] } );
						aoData.push( { "name": "iSortDir_"+(i+iFixed),  "value": oSettings.aaSorting[i][1] } );
					}
				}
				
				oSettings.fnServerData( oSettings.sAjaxSource, aoData, function(json) {
					_fnAjaxUpdateDraw( oSettings, json );
				} );
				return false;
			}
			else
			{
				return true;
			}
		}
		
		/*
		 * Function: _fnAjaxUpdateDraw
		 * Purpose:  Data the data from the server (nuking the old) and redraw the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           object:json - json data return from the server.
		 *             The following must be defined:
		 *               iTotalRecords, iTotalDisplayRecords, aaData
		 *             The following may be defined:
		 *               sColumns
		 */
		function _fnAjaxUpdateDraw ( oSettings, json )
		{
            
            aoJSON = json[oSettings.sJSONDataElement];
            
			if ( typeof aoJSON.sEcho != 'undefined' )
			{
				/* Protect against old returns over-writing a new one. Possible when you get
				 * very fast interaction, and later queires are completed much faster
				 */
				if ( aoJSON.sEcho*1 < oSettings.iServerDraw )
				{
					return;
				}
				else
				{
					oSettings.iServerDraw = aoJSON.sEcho * 1;
				}
			}
			
			_fnClearTable( oSettings );
			oSettings._iRecordsTotal = aoJSON.iTotalRecords;
			oSettings._iRecordsDisplay = aoJSON.iTotalDisplayRecords;
			
			/* Determine if reordering is required */
			var sOrdering = _fnColumnOrdering(oSettings);
			var bReOrder = (aoJSON.sColumns != 'undefined' && sOrdering !== "" && aoJSON.sColumns != sOrdering );
			if ( bReOrder )
			{
				var aiIndex = _fnReOrderIndex( oSettings, aoJSON.sColumns );
			}
			
			for ( var i=0, iLen=aoJSON.aaData.length ; i<iLen ; i++ )
			{
				if ( bReOrder )
				{
					/* If we need to re-order, then create a new array with the correct order and add it */
					var aData = [];
					for ( var j=0, jLen=oSettings.aoColumns.length ; j<jLen ; j++ )
					{
						aData.push( aoJSON.aaData[i][ aiIndex[j] ] );
					}
					_fnAddData( oSettings, aData );
				}
				else
				{
					/* No re-order required, sever got it "right" - just straight add */
					_fnAddData( oSettings, aoJSON.aaData[i] );
				}
			}
			oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
			
			oSettings.bAjaxDataGet = false;
			_fnDraw( oSettings );
			oSettings.bAjaxDataGet = true;
			_fnProcessingDisplay( oSettings, false );
		}
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Options (features) HTML
		 */
		
		/*
		 * Function: _fnAddOptionsHtml
		 * Purpose:  Add the options to the page HTML for the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnAddOptionsHtml ( oSettings )
		{
			/*
			 * Create a temporary, empty, div which we can later on replace with what we have generated
			 * we do it this way to rendering the 'options' html offline - speed :-)
			 */
			var nHolding = document.createElement( 'div' );
			oSettings.nTable.parentNode.insertBefore( nHolding, oSettings.nTable );
			
			/* 
			 * All DataTables are wrapped in a div - this is not currently optional - backwards 
			 * compatability. It can be removed if you don't want it.
			 */
			var nWrapper = document.createElement( 'div' );
			nWrapper.className = "dataTables_wrapper";
			if ( oSettings.sTableId !== '' )
			{
				nWrapper.setAttribute( 'id', oSettings.sTableId+'_wrapper' );
			}
			
			/* Track where we want to insert the option */
			var nInsertNode = nWrapper;
			
			/* IE don't treat strings as arrays */
			var sDom = oSettings.sDomPositioning.split('');
			
			/* Loop over the user set positioning and place the elements as needed */
			var nTmp;
			for ( var i=0 ; i<sDom.length ; i++ )
			{
				var cOption = sDom[i];
				
				if ( cOption == '<' )
				{
					/* New container div */
					var nNewNode = document.createElement( 'div' );
					
					/* Check to see if we should append a class name to the container */
					var cNext = sDom[i+1];
					if ( cNext == "'" || cNext == '"' )
					{
						var sClass = "";
						var j = 2;
						while ( sDom[i+j] != cNext )
						{
							sClass += sDom[i+j];
							j++;
						}
						nNewNode.className = sClass;
						i += j; /* Move along the position array */
					}
					
					nInsertNode.appendChild( nNewNode );
					nInsertNode = nNewNode;
				}
				else if ( cOption == '>' )
				{
					/* End container div */
					nInsertNode = nInsertNode.parentNode;
				}
				else if ( cOption == 'l' && oSettings.oFeatures.bPaginate && oSettings.oFeatures.bLengthChange )
				{
					/* Length */
					nTmp = _fnFeatureHtmlLength( oSettings );
					oSettings.anFeatures[cOption] = nTmp;
					nInsertNode.appendChild( nTmp );
				}
				else if ( cOption == 'f' && oSettings.oFeatures.bFilter )
				{
					/* Filter */
					nTmp = _fnFeatureHtmlFilter( oSettings );
					oSettings.anFeatures[cOption] = nTmp;
					nInsertNode.appendChild( nTmp );
				}
				else if ( cOption == 'r' && oSettings.oFeatures.bProcessing )
				{
					/* pRocessing */
                    // disabled since we're using the ula.notice for processing
                    // notification
					// nTmp = _fnFeatureHtmlProcessing( oSettings );
					// oSettings.anFeatures[cOption] = nTmp;
					// nInsertNode.appendChild( nTmp );
				}
				else if ( cOption == 't' )
				{
					/* Table */
					oSettings.anFeatures[cOption] = oSettings.nTable;
					nInsertNode.appendChild( oSettings.nTable );
				}
				else if ( cOption ==  'i' && oSettings.oFeatures.bInfo )
				{
					/* Info */
					nTmp = _fnFeatureHtmlInfo( oSettings );
					oSettings.anFeatures[cOption] = nTmp;
					nInsertNode.appendChild( nTmp );
				}
				else if ( cOption == 'p' && oSettings.oFeatures.bPaginate )
				{
					/* Pagination */
					nTmp = _fnFeatureHtmlPaginate( oSettings );
					oSettings.anFeatures[cOption] = nTmp;
					nInsertNode.appendChild( nTmp );
				}
				else if ( _oExt.aoFeatures.length !== 0 )
				{
					var aoFeatures = _oExt.aoFeatures;
					for ( var k=0, kLen=aoFeatures.length ; k<kLen ; k++ )
					{
						if ( cOption == aoFeatures[k].cFeature )
						{
							nTmp = aoFeatures[k].fnInit( oSettings );
							oSettings.anFeatures[cOption] = nTmp;
							nInsertNode.appendChild( nTmp );
							break;
						}
					}
				}
			}
			
			/* Built our DOM structure - replace the holding div with what we want */
			nHolding.parentNode.replaceChild( nWrapper, nHolding );
		}
		
		/*
		 * Function: _fnFeatureHtmlFilter
		 * Purpose:  Generate the node required for filtering text
		 * Returns:  node
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnFeatureHtmlFilter ( oSettings )
		{
			var nFilter = document.createElement( 'div' );
			if ( oSettings.sTableId !== '' )
			{
				nFilter.setAttribute( 'id', oSettings.sTableId+'_filter' );
			}
			nFilter.className = "dataTables_filter";
			var sSpace = oSettings.oLanguage.sSearch==="" ? "" : " ";
			nFilter.innerHTML = oSettings.oLanguage.sSearch+sSpace+'<input type="text" mor_default="Search Results..."/>';
			
			var jqFilter = $("input", nFilter);
			jqFilter.val( oSettings.oPreviousSearch.sSearch.replace('"','&quot;') );
			jqFilter.keyup( function(e) {
				_fnFilterComplete( oSettings, { 
					"sSearch": this.value, 
					"bEscapeRegex": oSettings.oPreviousSearch.bEscapeRegex 
				} );
			} );
			
			return nFilter;
		}
		
		/*
		 * Function: _fnFeatureHtmlInfo
		 * Purpose:  Generate the node required for the info display
		 * Returns:  node
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnFeatureHtmlInfo ( oSettings )
		{
			var nInfo = document.createElement( 'div' );
			if ( oSettings.sTableId !== '' )
			{
				nInfo.setAttribute( 'id', oSettings.sTableId+'_info' );
			}
			nInfo.className = "dataTables_info";
			return nInfo;
		}
		
		/*
		 * Function: _fnFeatureHtmlPaginate
		 * Purpose:  Generate the node required for default pagination
		 * Returns:  node
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnFeatureHtmlPaginate ( oSettings )
		{
			var nPaginate = document.createElement( 'div' );
			nPaginate.className = "dataTables_paginate paging_"+oSettings.sPaginationType;
			oSettings.anFeatures.p = nPaginate; /* Need this stored in order to call paging plug-ins */
			
			_oExt.oPagination[ oSettings.sPaginationType ].fnInit( oSettings, function( oSettings ) {
				_fnCalculateEnd( oSettings );
				_fnDraw( oSettings );
			} );
			return nPaginate;
		}
		
		/*
		 * Function: _fnFeatureHtmlLength
		 * Purpose:  Generate the node required for user display length changing
		 * Returns:  node
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnFeatureHtmlLength ( oSettings )
		{
			/* This can be overruled by not using the _MENU_ var/macro in the language variable */
			var sName = (oSettings.sTableId === "") ? "" : 'name="'+oSettings.sTableId+'_length"';
			var sStdMenu = 
				'<select size="1" '+sName+'>'+
					'<option value="10">10</option>'+
					'<option value="25">25</option>'+
					'<option value="50">50</option>'+
					'<option value="100">100</option>'+
				'</select>';
			
			var nLength = document.createElement( 'div' );
			if ( oSettings.sTableId !== '' )
			{
				nLength.setAttribute( 'id', oSettings.sTableId+'_length' );
			}
			nLength.className = "dataTables_length";
			nLength.innerHTML = oSettings.oLanguage.sLengthMenu.replace( '_MENU_', sStdMenu );
			
			/*
			 * Set the length to the current display length - thanks to Andrea Pavlovic for this fix,
			 * and Stefan Skopnik for fixing the fix!
			 */
			$('select option[value="'+oSettings._iDisplayLength+'"]',nLength).attr("selected",true);
			
			$('select', nLength).change( function(e) {
				oSettings._iDisplayLength = parseInt($(this).val(), 10);
				
				_fnCalculateEnd( oSettings );
				
				/* If we have space to show extra rows (backing up from the end point - then do so */
				if ( oSettings._iDisplayEnd == oSettings.aiDisplay.length )
				{
					oSettings._iDisplayStart = oSettings._iDisplayEnd - oSettings._iDisplayLength;
					if ( oSettings._iDisplayStart < 0 )
					{
						oSettings._iDisplayStart = 0;
					}
				}
				
				if ( oSettings._iDisplayLength == -1 )
				{
					oSettings._iDisplayStart = 0;
				}
				
				_fnDraw( oSettings );
			} );
			
			return nLength;
		}
		
		/*
		 * Function: _fnFeatureHtmlProcessing
		 * Purpose:  Generate the node required for the processing node
		 * Returns:  node
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnFeatureHtmlProcessing ( oSettings )
		{
			var nProcessing = document.createElement( 'div' );
			
			if ( oSettings.sTableId !== '' )
			{
				nProcessing.setAttribute( 'id', oSettings.sTableId+'_processing' );
			}
			nProcessing.innerHTML = oSettings.oLanguage.sProcessing;
			nProcessing.className = "dataTables_processing";
			oSettings.nTable.parentNode.insertBefore( nProcessing, oSettings.nTable );
			
			return nProcessing;
		}

        /**
         * Replace the div with the blocking ui we use
         */
        function _fnFeatureHtmlProcessing ( oSettings )
		{
            return null; //mor.notice.showMessage('Loading ...', mor.notice.types.loading);
		}
		
		/*
		 * Function: _fnProcessingDisplay
		 * Purpose:  Display or hide the processing indicator
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           bool:
		 *   true - show the processing indicator
		 *   false - don't show
		 */
		function _fnProcessingDisplay ( oSettings, bShow )
		{
			if ( oSettings.oFeatures.bProcessing )
			{
                if (bShow) {
                    mor.notice.showMessage('Loading ...', mor.notice.types.loading);
                } else {
                    mor.notice.hideMessage();
                }
				//oSettings.anFeatures.r.style.visibility = bShow ? "visible" : "hidden";
			}
		}
		
		
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Filtering
		 */
		
		/*
		 * Function: _fnFilterComplete
		 * Purpose:  Filter the table using both the global filter and column based filtering
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           object:oSearch: search information
		 *           int:iForce - optional - force a research of the master array (1) or not (undefined or 0)
		 */
		function _fnFilterComplete ( oSettings, oInput, iForce )
		{
			/* Filter on everything */
			_fnFilter( oSettings, oInput.sSearch, iForce, oInput.bEscapeRegex );
			
			/* Now do the individual column filter */
			for ( var i=0 ; i<oSettings.aoPreSearchCols.length ; i++ )
			{
				_fnFilterColumn( oSettings, oSettings.aoPreSearchCols[i].sSearch, i, 
					oSettings.aoPreSearchCols[i].bEscapeRegex );
			}
			
			/* Custom filtering */
			if ( _oExt.afnFiltering.length !== 0 )
			{
				_fnFilterCustom( oSettings );
			}
			
			/* Redraw the table */
			if ( typeof oSettings.iInitDisplayStart != 'undefined' && oSettings.iInitDisplayStart != -1 )
			{
				oSettings._iDisplayStart = oSettings.iInitDisplayStart;
				oSettings.iInitDisplayStart = -1;
			}
			else
			{
				oSettings._iDisplayStart = 0;
			}
			_fnCalculateEnd( oSettings );
			_fnDraw( oSettings );
			
			/* Rebuild search array 'offline' */
			_fnBuildSearchArray( oSettings, 0 );
		}
		
		/*
		 * Function: _fnFilterCustom
		 * Purpose:  Apply custom filtering functions
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnFilterCustom( oSettings )
		{
			var afnFilters = _oExt.afnFiltering;
			for ( var i=0, iLen=afnFilters.length ; i<iLen ; i++ )
			{
				var iCorrector = 0;
				for ( var j=0, jLen=oSettings.aiDisplay.length ; j<jLen ; j++ )
				{
					var iDisIndex = oSettings.aiDisplay[j-iCorrector];
					
					/* Check if we should use this row based on the filtering function */
					if ( !afnFilters[i]( oSettings, oSettings.aoData[iDisIndex]._aData, iDisIndex ) )
					{
						oSettings.aiDisplay.splice( j-iCorrector, 1 );
						iCorrector++;
					}
				}
			}
		}
		
		/*
		 * Function: _fnFilterColumn
		 * Purpose:  Filter the table on a per-column basis
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           string:sInput - string to filter on
		 *           int:iColumn - column to filter
		 *           bool:bEscapeRegex - escape regex or not
		 */
		function _fnFilterColumn ( oSettings, sInput, iColumn, bEscapeRegex )
		{
			if ( sInput === "" )
			{
				return;
			}
			
			var iIndexCorrector = 0;
			var sRegexMatch = bEscapeRegex ? _fnEscapeRegex( sInput ) : sInput;
			var rpSearch = new RegExp( sRegexMatch, "i" );
			
			for ( var i=oSettings.aiDisplay.length-1 ; i>=0 ; i-- )
			{
				var sData = _fnDataToSearch( oSettings.aoData[ oSettings.aiDisplay[i] ]._aData[iColumn],
					oSettings.aoColumns[iColumn].sType );
				if ( ! rpSearch.test( sData ) )
				{
					oSettings.aiDisplay.splice( i, 1 );
					iIndexCorrector++;
				}
			}
		}
		
		/*
		 * Function: _fnFilter
		 * Purpose:  Filter the data table based on user input and draw the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           string:sInput - string to filter on
		 *           int:iForce - optional - force a research of the master array (1) or not (undefined or 0)
		 *           bool:bEscapeRegex - escape regex or not
		 */
		function _fnFilter( oSettings, sInput, iForce, bEscapeRegex )
		{
			var i;
			
			/* Check if we are forcing or not - optional parameter */
			if ( typeof iForce == 'undefined' || iForce === null )
			{
				iForce = 0;
			}
			
			/* Need to take account of custom filtering functions always */
			if ( _oExt.afnFiltering.length !== 0 )
			{
				iForce = 1;
			}
			
			/* Generate the regular expression to use. Something along the lines of:
			 * ^(?=.*?\bone\b)(?=.*?\btwo\b)(?=.*?\bthree\b).*$
			 */
			var asSearch = bEscapeRegex ?
				_fnEscapeRegex( sInput ).split( ' ' ) :
				sInput.split( ' ' );
			var sRegExpString = '^(?=.*?'+asSearch.join( ')(?=.*?' )+').*$';
			var rpSearch = new RegExp( sRegExpString, "i" ); /* case insensitive */
			
			/*
			 * If the input is blank - we want the full data set
			 */
			if ( sInput.length <= 0 )
			{
				oSettings.aiDisplay.splice( 0, oSettings.aiDisplay.length);
				oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
			}
			else
			{
				/*
				 * We are starting a new search or the new search string is smaller 
				 * then the old one (i.e. delete). Search from the master array
			 	 */
				if ( oSettings.aiDisplay.length == oSettings.aiDisplayMaster.length ||
					   oSettings.oPreviousSearch.sSearch.length > sInput.length || iForce == 1 ||
					   sInput.indexOf(oSettings.oPreviousSearch.sSearch) !== 0 )
				{
					/* Nuke the old display array - we are going to rebuild it */
					oSettings.aiDisplay.splice( 0, oSettings.aiDisplay.length);
					
					/* Force a rebuild of the search array */
					_fnBuildSearchArray( oSettings, 1 );
					
					/* Search through all records to populate the search array
					 * The the oSettings.aiDisplayMaster and asDataSearch arrays have 1 to 1 
					 * mapping
					 */
					for ( i=0 ; i<oSettings.aiDisplayMaster.length ; i++ )
					{
						if ( rpSearch.test(oSettings.asDataSearch[i]) )
						{
							oSettings.aiDisplay.push( oSettings.aiDisplayMaster[i] );
						}
					}
			  }
			  else
				{
			  	/* Using old search array - refine it - do it this way for speed
			  	 * Don't have to search the whole master array again
			 		 */
			  	var iIndexCorrector = 0;
			  	
			  	/* Search the current results */
			  	for ( i=0 ; i<oSettings.asDataSearch.length ; i++ )
					{
			  		if ( ! rpSearch.test(oSettings.asDataSearch[i]) )
						{
			  			oSettings.aiDisplay.splice( i-iIndexCorrector, 1 );
			  			iIndexCorrector++;
			  		}
			  	}
			  }
			}
			oSettings.oPreviousSearch.sSearch = sInput;
			oSettings.oPreviousSearch.bEscapeRegex = bEscapeRegex;
		}
		
		
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Sorting
		 */
		
		/*
	 	 * Function: _fnSort
		 * Purpose:  Change the order of the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           bool:bApplyClasses - optional - should we apply classes or not
		 * Notes:    We always sort the master array and then apply a filter again
		 *   if it is needed. This probably isn't optimal - but atm I can't think
		 *   of any other way which is (each has disadvantages)
		 */
		function _fnSort ( oSettings, bApplyClasses )
		{
			/*
			 * Funny one this - we want to sort aiDisplayMaster - but according to aoData[]._aData
			 *
			 * function _fnSortText ( a, b )
			 * {
			 * 	var iTest;
			 * 	var oSort = _oExt.oSort;
			 * 	
			 * 	iTest = oSort['string-asc']( aoData[ a ]._aData[ COL ], aoData[ b ]._aData[ COL ] );
			 * 	if ( iTest === 0 )
			 * 		...
			 * }
			 */
			
			/* Here is what we are looking to achieve here (custom sort functions add complication...)
			 * function _fnSortText ( a, b )
			 * {
			 * 	var iTest;
			 *  var oSort = _oExt.oSort;
			 * 	iTest = oSort['string-asc']( a[0], b[0] );
			 * 	if ( iTest === 0 )
			 * 		iTest = oSort['string-asc']( a[1], b[1] );
			 * 		if ( iTest === 0 )
			 * 			iTest = oSort['string-asc']( a[2], b[2] );
			 * 	
			 * 	return iTest;
			 * }
			 */
			var aaSort = [];
			var oSort = _oExt.oSort;
			var aoData = oSettings.aoData;
			var iDataSort;
			var iDataType;
			var i;
			
			if ( oSettings.aaSorting.length !== 0 || oSettings.aaSortingFixed !== null )
			{
				if ( oSettings.aaSortingFixed !== null )
				{
					aaSort = oSettings.aaSortingFixed.concat( oSettings.aaSorting );
				}
				else
				{
					aaSort = oSettings.aaSorting.slice();
				}
				
				if ( !window.runtime )
				{
					var fnLocalSorting;
					var sDynamicSort = "fnLocalSorting = function(a,b){"+
						"var iTest;";
					
					for ( i=0 ; i<aaSort.length-1 ; i++ )
					{
						iDataSort = oSettings.aoColumns[ aaSort[i][0] ].iDataSort;
						iDataType = oSettings.aoColumns[ iDataSort ].sType;
						sDynamicSort += "iTest = oSort['"+iDataType+"-"+aaSort[i][1]+"']"+
							"( aoData[a]._aData["+iDataSort+"], aoData[b]._aData["+iDataSort+"] ); if ( iTest === 0 )";
					}
					
					iDataSort = oSettings.aoColumns[ aaSort[aaSort.length-1][0] ].iDataSort;
					iDataType = oSettings.aoColumns[ iDataSort ].sType;
					sDynamicSort += "iTest = oSort['"+iDataType+"-"+aaSort[aaSort.length-1][1]+"']"+
						"( aoData[a]._aData["+iDataSort+"], aoData[b]._aData["+iDataSort+"] ); return iTest;}";
					
					/* The eval has to be done to a variable for IE */
					eval( sDynamicSort );
					oSettings.aiDisplayMaster.sort( fnLocalSorting );
				}
				else
				{
					/*
					 * Support for Adobe AIR - AIR doesn't allow eval with a function
					 * Note that for reasonable sized data sets this method is around 1.5 times slower than
					 * the eval above (hence why it is not used all the time). Oddly enough, it is ever so
					 * slightly faster for very small sets (presumably the eval has overhead).
					 *   Single column (1083 records) - eval: 32mS   AIR: 38mS
					 *   Two columns (1083 records) -   eval: 55mS   AIR: 66mS
					 */
					
					/* Build a cached array so the sort doesn't have to process this stuff on every call */
					var aAirSort = [];
					var iLen = aaSort.length;
					for ( i=0 ; i<iLen ; i++ )
					{
						iDataSort = oSettings.aoColumns[ aaSort[i][0] ].iDataSort;
						aAirSort.push( [
							iDataSort,
							oSettings.aoColumns[ iDataSort ].sType+'-'+aaSort[i][1]
						] );
					}
					
					oSettings.aiDisplayMaster.sort( function (a,b) {
						var iTest;
						for ( var i=0 ; i<iLen ; i++ )
						{
							iTest = oSort[ aAirSort[i][1] ]( aoData[a]._aData[aAirSort[i][0]], aoData[b]._aData[aAirSort[i][0]] );
							if ( iTest !== 0 )
							{
								return iTest;
							}
						}
						return 0;
					} );
				}
			}
			
			/* Alter the sorting classes to take account of the changes */
			if ( typeof bApplyClasses == 'undefined' || bApplyClasses )
			{
				_fnSortingClasses( oSettings );
			}
			
			/* Copy the master data into the draw array and re-draw */
			if ( oSettings.oFeatures.bFilter )
			{
				/* _fnFilter() will redraw the table for us */
				_fnFilterComplete( oSettings, oSettings.oPreviousSearch, 1 );
			}
			else
			{
				oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
				oSettings._iDisplayStart = 0; /* reset display back to page 0 */
				_fnCalculateEnd( oSettings );
				_fnDraw( oSettings );
			}
		}
		
		/*
		 * Function: _fnSortingClasses
		 * Purpose:  Set the sortting classes on the header
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnSortingClasses( oSettings )
		{
			var i;
			var aaSort;
			var iColumns = oSettings.aoColumns.length;
			for ( i=0 ; i<iColumns ; i++ )
			{
				$(oSettings.aoColumns[i].nTh).removeClass( "sorting_asc sorting_desc sorting" );
			}
			
			if ( oSettings.aaSortingFixed !== null )
			{
				aaSort = oSettings.aaSortingFixed.concat( oSettings.aaSorting );
			}
			else
			{
				aaSort = oSettings.aaSorting.slice();
			}
			
			/* Apply the required classes to the header */
			for ( i=0 ; i<oSettings.aoColumns.length ; i++ )
			{
				if ( oSettings.aoColumns[i].bSortable && oSettings.aoColumns[i].bVisible )
				{
					var sClass = "sorting";
					for ( var j=0 ; j<aaSort.length ; j++ )
					{
						if ( aaSort[j][0] == i )
						{
							sClass = ( aaSort[j][1] == "asc" ) ?
								"sorting_asc" : "sorting_desc";
							break;
						}
					}
					$(oSettings.aoColumns[i].nTh).addClass( sClass );
				}
			}
			
			/* 
			 * Apply the required classes to the table body
			 * Note that this is given as a feature switch since it can significantly slow down a sort
			 * on large data sets (adding and removing of classes is always slow at the best of times..)
			 */
			if ( oSettings.oFeatures.bSortClasses )
			{
				var nTrs = _fnGetTrNodes( oSettings );
				$('td', nTrs).removeClass( 'sorting_1 sorting_2 sorting_3' );
				
				var iClass = 1;
				for ( i=0 ; i<aaSort.length ; i++ )
				{
					var iVis = _fnColumnIndexToVisible(oSettings, aaSort[i][0]);
					if ( iVis !== null )
					{
						/* Limit the number of classes to three */
						if ( iClass <= 2 )
						{
							$('td:eq('+iVis+')', nTrs).addClass( 'sorting_'+iClass );
						}
						else
						{
							$('td:eq('+iVis+')', nTrs).addClass( 'sorting_3' );
						}
						iClass++;
					}
				}
			}
		}
		
		/*
		 * Function: _fnVisibleToColumnIndex
		 * Purpose:  Covert the index of a visible column to the index in the data array (take account
		 *   of hidden columns)
		 * Returns:  int:i - the data index
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnVisibleToColumnIndex( oSettings, iMatch )
		{
			var iColumn = -1;
			
			for ( var i=0 ; i<oSettings.aoColumns.length ; i++ )
			{
				if ( oSettings.aoColumns[i].bVisible === true )
				{
					iColumn++;
				}
				
				if ( iColumn == iMatch )
				{
					return i;
				}
			}
			
			return null;
		}
		
		/*
		 * Function: _fnColumnIndexToVisible
		 * Purpose:  Covert the index of an index in the data array and convert it to the visible
		 *   column index (take account of hidden columns)
		 * Returns:  int:i - the data index
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnColumnIndexToVisible( oSettings, iMatch )
		{
			var iVisible = -1;
			for ( var i=0 ; i<oSettings.aoColumns.length ; i++ )
			{
				if ( oSettings.aoColumns[i].bVisible === true )
				{
					iVisible++;
				}
				
				if ( i == iMatch )
				{
					return oSettings.aoColumns[i].bVisible === true ? iVisible : null;
				}
			}
			
			return null;
		}
		
		/*
		 * Function: _fnVisbleColumns
		 * Purpose:  Get the number of visible columns
		 * Returns:  int:i - the number of visible columns
		 * Inputs:   object:oS - dataTables settings object
		 */
		function _fnVisbleColumns( oS )
		{
			var iVis = 0;
			for ( var i=0 ; i<oS.aoColumns.length ; i++ )
			{
				if ( oS.aoColumns[i].bVisible === true )
				{
					iVis++;
				}
			}
			return iVis;
		}
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Support functions
		 */
		
		/*
		 * Function: _fnBuildSearchArray
		 * Purpose:  Create an array which can be quickly search through
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           int:iMaster - use the master data array - optional
		 */
		function _fnBuildSearchArray ( oSettings, iMaster )
		{
			/* Clear out the old data */
			oSettings.asDataSearch.splice( 0, oSettings.asDataSearch.length );
			
			var aArray = (typeof iMaster != 'undefined' && iMaster == 1) ?
			 	oSettings.aiDisplayMaster : oSettings.aiDisplay;
			
			for ( var i=0, iLen=aArray.length ; i<iLen ; i++ )
			{
				oSettings.asDataSearch[i] = '';
				for ( var j=0, jLen=oSettings.aoColumns.length ; j<jLen ; j++ )
				{
					if ( oSettings.aoColumns[j].bSearchable )
					{
						var sData = oSettings.aoData[ aArray[i] ]._aData[j];
						oSettings.asDataSearch[i] += _fnDataToSearch( sData, oSettings.aoColumns[j].sType )+' ';
					}
				}
			}
		}
		
		/*
		 * Function: _fnDataToSearch
		 * Purpose:  Convert raw data into something that the user can search on
		 * Returns:  string: - search string
		 * Inputs:   string:sData - data to be modified
		 *           string:sType - data type
		 */
		function _fnDataToSearch ( sData, sType )
		{
			
			if ( typeof _oExt.ofnSearch[sType] == "function" )
			{
				return _oExt.ofnSearch[sType]( sData );
			}
			else if ( sType == "html" )
			{
				return sData.replace(/\n/g," ").replace( /<.*?>/g, "" );
			}
			else if ( typeof sData == "string" )
			{
				return sData.replace(/\n/g," ");
			}
			return sData;
		}
		
		/*
		 * Function: _fnCalculateEnd
		 * Purpose:  Rcalculate the end point based on the start point
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnCalculateEnd( oSettings )
		{
            
			if ( oSettings.oFeatures.bPaginate === false )
			{
				oSettings._iDisplayEnd = oSettings.aiDisplay.length;
			}
			else
			{
				/* Set the end point of the display - based on how many elements there are
				 * still to display
				 */
				if ( oSettings._iDisplayStart + oSettings._iDisplayLength > oSettings.aiDisplay.length ||
					   oSettings._iDisplayLength == -1 )
				{
					oSettings._iDisplayEnd = oSettings.aiDisplay.length;
				}
				else
				{
					oSettings._iDisplayEnd = oSettings._iDisplayStart + oSettings._iDisplayLength;
				}
			}
		}
		
		/*
		 * Function: _fnConvertToWidth
		 * Purpose:  Convert a CSS unit width to pixels (e.g. 2em)
		 * Returns:  int:iWidth - width in pixels
		 * Inputs:   string:sWidth - width to be converted
		 *           node:nParent - parent to get the with for (required for
		 *             relative widths) - optional
		 */
		function _fnConvertToWidth ( sWidth, nParent )
		{
			if ( !sWidth || sWidth === null || sWidth === '' )
			{
				return 0;
			}
			
			if ( typeof nParent == "undefined" )
			{
				nParent = document.getElementsByTagName('body')[0];
			}
			
			var iWidth;
			var nTmp = document.createElement( "div" );
			nTmp.style.width = sWidth;
			
			nParent.appendChild( nTmp );
			iWidth = nTmp.offsetWidth;
			nParent.removeChild( nTmp );
			
			return ( iWidth );
		}
		
		/*
		 * Function: _fnCalculateColumnWidths
		 * Purpose:  Calculate the width of columns for the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnCalculateColumnWidths ( oSettings )
		{
			var iTableWidth = oSettings.nTable.offsetWidth;
			var iTotalUserIpSize = 0;
			var iTmpWidth;
			var iVisibleColumns = 0;
			var iColums = oSettings.aoColumns.length;
			var i;
			var oHeaders = $('thead th', oSettings.nTable);
			
			/* Convert any user input sizes into pixel sizes */
			for ( i=0 ; i<iColums ; i++ )
			{
				if ( oSettings.aoColumns[i].bVisible )
				{
					iVisibleColumns++;
					
					if ( oSettings.aoColumns[i].sWidth !== null )
					{
						iTmpWidth = _fnConvertToWidth( oSettings.aoColumns[i].sWidth, 
							oSettings.nTable.parentNode );
						
						/* Total up the user defined widths for later calculations */
						iTotalUserIpSize += iTmpWidth;
						
						oSettings.aoColumns[i].sWidth = iTmpWidth+"px";
					}
				}
			}
			
			/* If the number of columns in the DOM equals the number that we
			 * have to process in dataTables, then we can use the offsets that are
			 * created by the web-browser. No custom sizes can be set in order for
			 * this to happen
			 */
			if ( iColums == oHeaders.length && iTotalUserIpSize === 0 && iVisibleColumns == iColums )
			{
				for ( i=0 ; i<oSettings.aoColumns.length ; i++ )
				{
					oSettings.aoColumns[i].sWidth = oHeaders[i].offsetWidth+"px";
				}
			}
			else
			{
				/* Otherwise we are going to have to do some calculations to get
				 * the width of each column. Construct a 1 row table with the maximum
				 * string sizes in the data, and any user defined widths
				 */
				var nCalcTmp = oSettings.nTable.cloneNode( false );
				nCalcTmp.setAttribute( "id", '' );
				
				var sTableTmp = '<table class="'+nCalcTmp.className+'">';
				var sCalcHead = "<tr>";
				var sCalcHtml = "<tr>";
				
				/* Construct a tempory table which we will inject (invisibly) into
				 * the dom - to let the browser do all the hard word
				 */
				for ( i=0 ; i<iColums ; i++ )
				{
					if ( oSettings.aoColumns[i].bVisible )
					{
						sCalcHead += '<th>'+oSettings.aoColumns[i].sTitle+'</th>';
						
						if ( oSettings.aoColumns[i].sWidth !== null )
						{
							var sWidth = '';
							if ( oSettings.aoColumns[i].sWidth !== null )
							{
								sWidth = ' style="width:'+oSettings.aoColumns[i].sWidth+';"';
							}
							
							sCalcHtml += '<td'+sWidth+' tag_index="'+i+'">'+fnGetMaxLenString( oSettings, i)+'</td>';
						}
						else
						{
							sCalcHtml += '<td tag_index="'+i+'">'+fnGetMaxLenString( oSettings, i)+'</td>';
						}
					}
				}
				
				sCalcHead += "</tr>";
				sCalcHtml += "</tr>";
				
				/* Create the tmp table node (thank you jQuery) */
				nCalcTmp = $( sTableTmp + sCalcHead + sCalcHtml +'</table>' )[0];
				nCalcTmp.style.width = iTableWidth + "px";
				nCalcTmp.style.visibility = "hidden";
				nCalcTmp.style.position = "absolute"; /* Try to aviod scroll bar */
				
				oSettings.nTable.parentNode.appendChild( nCalcTmp );
				
				var oNodes = $("td", nCalcTmp);
				var iIndex;
				
				/* Gather in the browser calculated widths for the rows */
				for ( i=0 ; i<oNodes.length ; i++ )
				{
					iIndex = oNodes[i].getAttribute('tag_index');
					
					oSettings.aoColumns[iIndex].sWidth = $("td", nCalcTmp)[i].offsetWidth +"px";
				}
				
				oSettings.nTable.parentNode.removeChild( nCalcTmp );
			}
		}
		
		/*
		 * Function: fnGetMaxLenString
		 * Purpose:  Get the maximum strlen for each data column
		 * Returns:  string: - max strlens for each column
		 * Inputs:   object:oSettings - dataTables settings object
		 *           int:iCol - column of interest
		 */
		function fnGetMaxLenString( oSettings, iCol )
		{
			var iMax = 0;
			var iMaxIndex = -1;
			
			for ( var i=0 ; i<oSettings.aoData.length ; i++ )
			{
				if ( oSettings.aoData[i]._aData[iCol].length > iMax )
				{
					iMax = oSettings.aoData[i]._aData[iCol].length;
					iMaxIndex = i;
				}
			}
			
			if ( iMaxIndex >= 0 )
			{
				return oSettings.aoData[iMaxIndex]._aData[iCol];
			}
			return '';
		}
		
		/*
		 * Function: _fnArrayCmp
		 * Purpose:  Compare two arrays
		 * Returns:  0 if match, 1 if length is different, 2 if no match
		 * Inputs:   array:aArray1 - first array
		 *           array:aArray2 - second array
		 */
		function _fnArrayCmp( aArray1, aArray2 )
		{
			if ( aArray1.length != aArray2.length )
			{
				return 1;
			}
			
			for ( var i=0 ; i<aArray1.length ; i++ )
			{
				if ( aArray1[i] != aArray2[i] )
				{
					return 2;
				}
			}
			
			return 0;
		}
		
		/*
		 * Function: _fnDetectType
		 * Purpose:  Get the sort type based on an input string
		 * Returns:  string: - type (defaults to 'string' if no type can be detected)
		 * Inputs:   string:sData - data we wish to know the type of
		 * Notes:    This function makes use of the DataTables plugin objct _oExt 
		 *   (.aTypes) such that new types can easily be added.
		 */
		function _fnDetectType( sData )
		{
			var aTypes = _oExt.aTypes;
			var iLen = aTypes.length;
			
			for ( var i=0 ; i<iLen ; i++ )
			{
				var sType = aTypes[i]( sData );
				if ( sType !== null )
				{
					return sType;
				}
			}
			
			return 'string';
		}
		
		/*
		 * Function: _fnSettingsFromNode
		 * Purpose:  Return the settings object for a particular table
		 * Returns:  object: Settings object - or null if not found
		 * Inputs:   node:nTable - table we are using as a dataTable
		 */
		function _fnSettingsFromNode ( nTable )
		{
			for ( var i=0 ; i<_aoSettings.length ; i++ )
			{
				if ( _aoSettings[i].nTable == nTable )
				{
					return _aoSettings[i];
				}
			}
			
			return null;
		}
		
		/*
		 * Function: _fnGetDataMaster
		 * Purpose:  Return an array with the full table data
		 * Returns:  array array:aData - Master data array
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnGetDataMaster ( oSettings )
		{
			var aData = [];
			var iLen = oSettings.aoData.length;
			for ( var i=0 ; i<iLen; i++ )
			{
				aData.push( oSettings.aoData[i]._aData );
			}
			return aData;
		}
		
		/*
		 * Function: _fnGetTrNodes
		 * Purpose:  Return an array with the TR nodes for the table
		 * Returns:  array array:aData - TR array
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnGetTrNodes ( oSettings )
		{
			var aNodes = [];
			var iLen = oSettings.aoData.length;
			for ( var i=0 ; i<iLen ; i++ )
			{
				aNodes.push( oSettings.aoData[i].nTr );
			}
			return aNodes;
		}
		
		/*
		 * Function: _fnEscapeRegex
		 * Purpose:  scape a string stuch that it can be used in a regular expression
		 * Returns:  string: - escaped string
		 * Inputs:   string:sVal - string to escape
		 */
		function _fnEscapeRegex ( sVal )
		{
			var acEscape = [ '/', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\', '$', '^' ];
		  var reReplace = new RegExp( '(\\' + acEscape.join('|\\') + ')', 'g' );
		  return sVal.replace(reReplace, '\\$1');
		}
		
		/*
		 * Function: _fnReOrderIndex
		 * Purpose:  Figure out how to reorder a display list
		 * Returns:  array int:aiReturn - index list for reordering
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnReOrderIndex ( oSettings, sColumns )
		{
			var aColumns = sColumns.split(',');
			var aiReturn = [];
			
			for ( var i=0, iLen=oSettings.aoColumns.length ; i<iLen ; i++ )
			{
				for ( var j=0 ; j<iLen ; j++ )
				{
					if ( oSettings.aoColumns[i].sName == aColumns[j] )
					{
						aiReturn.push( j );
						break;
					}
				}
			}
			
			return aiReturn;
		}
		
		/*
		 * Function: _fnColumnOrdering
		 * Purpose:  Get the column ordering that DataTables expects
		 * Returns:  string: - comma separated list of names
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnColumnOrdering ( oSettings )
		{
			var sNames = '';
			for ( var i=0, iLen=oSettings.aoColumns.length ; i<iLen ; i++ )
			{
				sNames += oSettings.aoColumns[i].sName+',';
			}
			if ( sNames.length == iLen )
			{
				return "";
			}
			return sNames.slice(0, -1);
		}
		
		/*
		 * Function: _fnClearTable
		 * Purpose:  Nuke the table
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnClearTable( oSettings )
		{
			oSettings.aoData.length = 0;
			oSettings.aiDisplayMaster.length = 0;
			oSettings.aiDisplay.length = 0;
			_fnCalculateEnd( oSettings );
		}
		
		/*
		 * Function: _fnSaveState
		 * Purpose:  Save the state of a table in a cookie such that the page can be reloaded
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 */
		function _fnSaveState ( oSettings )
		{
			if ( !oSettings.oFeatures.bStateSave )
			{
				return;
			}
			
			/* Store the interesting variables */
			var i;
			var sValue = "{";
			sValue += '"iStart": '+oSettings._iDisplayStart+',';
			sValue += '"iEnd": '+oSettings._iDisplayEnd+',';
			sValue += '"iLength": '+oSettings._iDisplayLength+',';
			sValue += '"sFilter": "'+oSettings.oPreviousSearch.sSearch.replace('"','\\"')+'",';
			sValue += '"sFilterEsc": '+oSettings.oPreviousSearch.bEscapeRegex+',';
			
			sValue += '"aaSorting": [ ';
			for ( i=0 ; i<oSettings.aaSorting.length ; i++ )
			{
				sValue += "["+oSettings.aaSorting[i][0]+",'"+oSettings.aaSorting[i][1]+"'],";
			}
			sValue = sValue.substring(0, sValue.length-1);
			sValue += "],";
			
			sValue += '"aaSearchCols": [ ';
			for ( i=0 ; i<oSettings.aoPreSearchCols.length ; i++ )
			{
				sValue += "['"+oSettings.aoPreSearchCols[i].sSearch.replace("'","\'")+
					"',"+oSettings.aoPreSearchCols[i].bEscapeRegex+"],";
			}
			sValue = sValue.substring(0, sValue.length-1);
			sValue += "],";
			
			sValue += '"abVisCols": [ ';
			for ( i=0 ; i<oSettings.aoColumns.length ; i++ )
			{
				sValue += oSettings.aoColumns[i].bVisible+",";
			}
			sValue = sValue.substring(0, sValue.length-1);
			sValue += "]";
			
			sValue += "}";
			_fnCreateCookie( "SpryMedia_DataTables_"+oSettings.sInstance, sValue, 
				oSettings.iCookieDuration );
		}
		
		/*
		 * Function: _fnLoadState
		 * Purpose:  Attempt to load a saved table state from a cookie
		 * Returns:  -
		 * Inputs:   object:oSettings - dataTables settings object
		 *           object:oInit - DataTables init object so we can override settings
		 */
		function _fnLoadState ( oSettings, oInit )
		{
			if ( !oSettings.oFeatures.bStateSave )
			{
				return;
			}
			
			var oData;
			var sData = _fnReadCookie( "SpryMedia_DataTables_"+oSettings.sInstance );
			if ( sData !== null && sData !== '' )
			{
				/* Try/catch the JSON eval - if it is bad then we ignore it */
				try
				{
					/* Use the JSON library for safety - if it is available */
					if ( typeof JSON == 'object' && typeof JSON.parse == 'function' )
					{
						/* DT 1.4.0 used single quotes for a string - JSON.parse doesn't allow this and throws
						 * an error. So for now we can do this. This can be removed in future it is just to
						 * allow the tranfrer to 1.4.1+ to occur
						 */
						oData = JSON.parse( sData.replace(/'/g, '"') );
					}
					else
					{
						oData = eval( '('+sData+')' );
					}
				}
				catch( e )
				{
					return;
				}
				
				/* Restore key features */
				oSettings._iDisplayStart = oData.iStart;
				oSettings.iInitDisplayStart = oData.iStart;
				oSettings._iDisplayEnd = oData.iEnd;
				oSettings._iDisplayLength = oData.iLength;
				oSettings.oPreviousSearch.sSearch = oData.sFilter;
				oSettings.aaSorting = oData.aaSorting.slice();
				
				/* Search filtering - global reference added in 1.4.1 */
				if ( typeof oData.sFilterEsc != 'undefined' )
				{
					oSettings.oPreviousSearch.bEscapeRegex = oData.sFilterEsc;
				}
				
				/* Column filtering - added in 1.5.0 beta 6 */
				if ( typeof oData.aaSearchCols != 'undefined' )
				{
					for ( var i=0 ; i<oData.aaSearchCols.length ; i++ )
					{
						oSettings.aoPreSearchCols[i] = {
							"sSearch": oData.aaSearchCols[i][0],
							"bEscapeRegex": oData.aaSearchCols[i][1]
						};
					}
				}
				
				/* Column visibility state - added in 1.5.0 beta 10 */
				if ( typeof oData.abVisCols != 'undefined' )
				{
					/* We need to override the settings in oInit for this */
					if ( typeof oInit.aoColumns == 'undefined' )
					{
						oInit.aoColumns = [];
					}
					
					for ( i=0 ; i<oData.abVisCols.length ; i++ )
					{
						if ( typeof oInit.aoColumns[i] == 'undefined' || oInit.aoColumns[i] === null )
						{
							oInit.aoColumns[i] = {};
						}
						
						oInit.aoColumns[i].bVisible = oData.abVisCols[i];
					}
				}
			}
		}
		
		/*
		 * Function: _fnCreateCookie
		 * Purpose:  Create a new cookie with a value to store the state of a table
		 * Returns:  -
		 * Inputs:   string:sName - name of the cookie to create
		 *           string:sValue - the value the cookie should take
		 *           int:iSecs - duration of the cookie
		 */
		function _fnCreateCookie ( sName, sValue, iSecs )
		{
			var date = new Date();
			date.setTime( date.getTime()+(iSecs*1000) );
			
			/* 
			 * Shocking but true - it would appear IE has major issues with having the path being
			 * set to anything but root. We need the cookie to be available based on the path, so we
			 * have to append the pathname to the cookie name. Appalling.
			 */
			sName += '_'+window.location.pathname.replace(/[\/:]/g,"").toLowerCase();
			
			document.cookie = sName+"="+sValue+"; expires="+date.toGMTString()+"; path=/";
		}
		
		/*
		 * Function: _fnReadCookie
		 * Purpose:  Read an old cookie to get a cookie with an old table state
		 * Returns:  string: - contents of the cookie - or null if no cookie with that name found
		 * Inputs:   string:sName - name of the cookie to read
		 */
		function _fnReadCookie ( sName )
		{
			var sNameEQ = sName +'_'+ window.location.pathname.replace(/[\/:]/g,"").toLowerCase() + "=";
			var sCookieContents = document.cookie.split(';');
			
			for( var i=0 ; i<sCookieContents.length ; i++ )
			{
				var c = sCookieContents[i];
				
				while (c.charAt(0)==' ')
				{
					c = c.substring(1,c.length);
				}
				
				if (c.indexOf(sNameEQ) === 0)
				{
					return c.substring(sNameEQ.length,c.length);
				}
			}
			return null;
		}
		
		/*
		 * Function: _fnGetUniqueThs
		 * Purpose:  Get an array of unique th elements, one for each column
		 * Returns:  array node:aReturn - list of unique ths
		 * Inputs:   node:nThead - The thead element for the table
		 */
		function _fnGetUniqueThs ( nThead )
		{
			var nTrs = nThead.getElementsByTagName('tr');
			
			/* Nice simple case */
			if ( nTrs.length == 1 )
			{
				return nTrs[0].getElementsByTagName('th');
			}
			
			/* Otherwise we need to figure out the layout array to get the nodes */
			var aLayout = [], aReturn = [];
			var ROWSPAN = 2, COLSPAN = 3;
			var i, j, k, iLen, jLen, iColumnShifted;
			var fnShiftCol = function ( a, i, j ) {
				while ( typeof a[i][j] != 'undefined' ) {
					j++;
				}
				return j;
			};
			var fnAddRow = function ( i ) {
				if ( typeof aLayout[i] == 'undefined' ) {
					aLayout[i] = [];
				}
			};
			
			/* Calculate a layout array */
			for ( i=0, iLen=nTrs.length ; i<iLen ; i++ )
			{
				fnAddRow( i );
				var iColumn = 0;
				var nTds = nTrs[i].getElementsByTagName('th');
				
				for ( j=0, jLen=nTds.length ; j<jLen ; j++ )
				{
					var iColspan = nTds[j].getAttribute('colspan') * 1;
					var iRowspan = nTds[j].getAttribute('rowspan') * 1;
					
					if ( !iColspan || iColspan===0 || iColspan===1 )
					{
						iColumnShifted = fnShiftCol( aLayout, i, iColumn );
						aLayout[i][iColumnShifted] = nTds[j];
						if ( iRowspan || iRowspan===0 || iRowspan===1 )
						{
							for ( k=1 ; k<iRowspan ; k++ )
							{
								fnAddRow( i+k );
								aLayout[i+k][iColumnShifted] = ROWSPAN;
							}
						}
						iColumn++;
					}
					else
					{
						iColumnShifted = fnShiftCol( aLayout, i, iColumn );
						for ( k=0 ; k<iColspan ; k++ )
						{
							aLayout[i][iColumnShifted+k] = COLSPAN;
						}
						iColumn += iColspan;
					}
				}
			}
			
			/* Convert the layout array into a node array */
			for ( i=0, iLen=aLayout.length ; i<iLen ; i++ )
			{
				for ( j=0, jLen=aLayout.length ; j<jLen ; j++ )
				{
					if ( typeof aLayout[j][i] == 'object' )
					{
						aReturn.push( aLayout[j][i] );
					}
				}
			}
			
			return aReturn;
		}
		
		/*
		 * Function: _fnMap
		 * Purpose:  See if a property is defined on one object, if so assign it to the other object
		 * Returns:  - (done by reference)
		 * Inputs:   object:oRet - target object
		 *           object:oSrc - source object
		 *           string:sName - property
		 *           string:sMappedName - name to map too - optional, sName used if not given
		 */
		function _fnMap( oRet, oSrc, sName, sMappedName )
		{
			if ( typeof sMappedName == 'undefined' )
			{
				sMappedName = sName;
			}
			if ( typeof oSrc[sName] != 'undefined' )
			{
				oRet[sMappedName] = oSrc[sName];
			}
		}
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * API
		 * 
		 * I'm not overly happy with this solution - I'd much rather that there was a way of getting
		 * a list of all the private functions and do what we need to dynamically - but that doesn't
		 * appear to be possible. Bonkers. A better solution would be to provide a 'bind' type object
		 * To do - bind type method in DTs 1.6.
		 */
		this.oApi._fnInitalise = _fnInitalise;
		this.oApi._fnLanguageProcess = _fnLanguageProcess;
		this.oApi._fnAddColumn = _fnAddColumn;
		this.oApi._fnAddData = _fnAddData;
		this.oApi._fnGatherData = _fnGatherData;
		this.oApi._fnDrawHead = _fnDrawHead;
		this.oApi._fnDraw = _fnDraw;
		this.oApi._fnAjaxUpdate = _fnAjaxUpdate;
		this.oApi._fnAddOptionsHtml = _fnAddOptionsHtml;
		this.oApi._fnFeatureHtmlFilter = _fnFeatureHtmlFilter;
		this.oApi._fnFeatureHtmlInfo = _fnFeatureHtmlInfo;
		this.oApi._fnFeatureHtmlPaginate = _fnFeatureHtmlPaginate;
		this.oApi._fnFeatureHtmlLength = _fnFeatureHtmlLength;
		this.oApi._fnFeatureHtmlProcessing = _fnFeatureHtmlProcessing;
		this.oApi._fnProcessingDisplay = _fnProcessingDisplay;
		this.oApi._fnFilterComplete = _fnFilterComplete;
		this.oApi._fnFilterColumn = _fnFilterColumn;
		this.oApi._fnFilter = _fnFilter;
		this.oApi._fnSortingClasses = _fnSortingClasses;
		this.oApi._fnVisibleToColumnIndex = _fnVisibleToColumnIndex;
		this.oApi._fnColumnIndexToVisible = _fnColumnIndexToVisible;
		this.oApi._fnVisbleColumns = _fnVisbleColumns;
		this.oApi._fnBuildSearchArray = _fnBuildSearchArray;
		this.oApi._fnDataToSearch = _fnDataToSearch;
		this.oApi._fnCalculateEnd = _fnCalculateEnd;
		this.oApi._fnConvertToWidth = _fnConvertToWidth;
		this.oApi._fnCalculateColumnWidths = _fnCalculateColumnWidths;
		this.oApi._fnArrayCmp = _fnArrayCmp;
		this.oApi._fnDetectType = _fnDetectType;
		this.oApi._fnGetDataMaster = _fnGetDataMaster;
		this.oApi._fnGetTrNodes = _fnGetTrNodes;
		this.oApi._fnEscapeRegex = _fnEscapeRegex;
		this.oApi._fnReOrderIndex = _fnReOrderIndex;
		this.oApi._fnColumnOrdering = _fnColumnOrdering;
		this.oApi._fnClearTable = _fnClearTable;
		this.oApi._fnSaveState = _fnSaveState;
		this.oApi._fnLoadState = _fnLoadState;
		this.oApi._fnCreateCookie = _fnCreateCookie;
		this.oApi._fnReadCookie = _fnReadCookie;
		this.oApi._fnGetUniqueThs = _fnGetUniqueThs;
		
		/* Want to be able to reference "this" inside the this.each function */
		var _that = this;
		
		
		/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
		 * Constructor
		 */
		return this.each(function()
		{
			/* Make a complete and independent copy of the settings object */
			var oSettings = new classSettings();
			_aoSettings.push( oSettings );
			
			var i=0, iLen;
			var bInitHandedOff = false;
			var bUsePassedData = false;
			
			/* Set the id */
			var sId = this.getAttribute( 'id' );
			if ( sId !== null )
			{
				oSettings.sTableId = sId;
				oSettings.sInstance = sId;
			}
			else
			{
				oSettings.sInstance = _oExt._oExternConfig.iNextUnique ++;
			}
			
			/* Set the table node */
			oSettings.nTable = this;
			
			/* Bind the API functions to the settings, so we can perform actions whenever oSettings is
			 * available
			 */
			oSettings.oApi = _that.oApi;
			
			/* Store the features that we have available */
			if ( typeof oInit != 'undefined' && oInit !== null )
			{
				_fnMap( oSettings.oFeatures, oInit, "bPaginate" );
				_fnMap( oSettings.oFeatures, oInit, "bLengthChange" );
				_fnMap( oSettings.oFeatures, oInit, "bFilter" );
				_fnMap( oSettings.oFeatures, oInit, "bSort" );
				_fnMap( oSettings.oFeatures, oInit, "bInfo" );
				_fnMap( oSettings.oFeatures, oInit, "bProcessing" );
				_fnMap( oSettings.oFeatures, oInit, "bAutoWidth" );
				_fnMap( oSettings.oFeatures, oInit, "bSortClasses" );
				_fnMap( oSettings.oFeatures, oInit, "bServerSide" );
				_fnMap( oSettings, oInit, "asStripClasses" );
				_fnMap( oSettings, oInit, "fnRowCallback" );
				_fnMap( oSettings, oInit, "fnHeaderCallback" );
				_fnMap( oSettings, oInit, "fnFooterCallback" );
				_fnMap( oSettings, oInit, "fnDrawCallback" );
				_fnMap( oSettings, oInit, "fnInitComplete" );
				_fnMap( oSettings, oInit, "fnServerData" );
				_fnMap( oSettings, oInit, "aaSorting" );
				_fnMap( oSettings, oInit, "aaSortingFixed" );
				_fnMap( oSettings, oInit, "sPaginationType" );
				_fnMap( oSettings, oInit, "sAjaxSource" );
				_fnMap( oSettings, oInit, "oAjaxBaseData" );
				_fnMap( oSettings, oInit, "sDom", "sDomPositioning" );
				_fnMap( oSettings, oInit, "oSearch", "oPreviousSearch" );
				_fnMap( oSettings, oInit, "aoSearchCols", "aoPreSearchCols" );
				_fnMap( oSettings, oInit, "iDisplayLength", "_iDisplayLength" );
				
				if ( typeof oInit.iDisplayStart != 'undefined' && 
				     typeof oSettings.iInitDisplayStart == 'undefined' ) {
					/* Display start point, taking into account the save saving */
					oSettings.iInitDisplayStart = oInit.iDisplayStart;
					oSettings._iDisplayStart = oInit.iDisplayStart;
				}
				
				/* Must be done after everything which can be overridden by a cookie! */
				if ( typeof oInit.bStateSave != 'undefined' )
				{
					oSettings.oFeatures.bStateSave = oInit.bStateSave;
					_fnLoadState( oSettings, oInit );
				}
				
				
				if ( typeof oInit.aaData != 'undefined' ) {
					bUsePassedData = true;
				}
				
				/* Backwards compatability */
				/* aoColumns / aoData - remove at some point... */
				if ( typeof oInit != 'undefined' && typeof oInit.aoData != 'undefined' )
				{
					oInit.aoColumns = oInit.aoData;
				}
				
				/* Language definitions */
				if ( typeof oInit.oLanguage != 'undefined' )
				{
					if ( typeof oInit.oLanguage.sUrl != 'undefined' && oInit.oLanguage.sUrl !== "" )
					{
						/* Get the language definitions from a file */
						oSettings.oLanguage.sUrl = oInit.oLanguage.sUrl;
						$.getJSON( oSettings.oLanguage.sUrl, null, function( json ) { 
							_fnLanguageProcess( oSettings, json, true ); } );
						bInitHandedOff = true;
					}
					else
					{
						_fnLanguageProcess( oSettings, oInit.oLanguage, false );
					}
				}
				/* Warning: The _fnLanguageProcess function is async to the remainder of this function due
				 * to the XHR. We use _bInitialised in _fnLanguageProcess() to check this the processing 
				 * below is complete. The reason for spliting it like this is optimisation - we can fire
				 * off the XHR (if needed) and then continue processing the data.
				 */
			}
			
			/* See if we should load columns automatically or use defined ones - a bit messy this... */
			var nThead = this.getElementsByTagName('thead');
			var nThs = nThead.length===0 ? null : _fnGetUniqueThs( nThead[0] );
			var bUseCols = typeof oInit != 'undefined' && typeof oInit.aoColumns != 'undefined';
			for ( i=0, iLen=bUseCols ? oInit.aoColumns.length : nThs.length ; i<iLen ; i++ )
			{
				var col = bUseCols ? oInit.aoColumns[i] : null;
				var n = nThs ? nThs[i] : null;
				_fnAddColumn( oSettings, col, n );
			}
			
			/* Sanity check that there is a thead and tfoot. If not let's just create them */
			if ( this.getElementsByTagName('thead').length === 0 )
			{
				this.appendChild( document.createElement( 'thead' ) );
			}
			
			if ( this.getElementsByTagName('tbody').length === 0 )
			{
				this.appendChild( document.createElement( 'tbody' ) );
			}
			
			/* Check if there is data passing into the constructor */
			if ( bUsePassedData )
			{
				for ( i=0 ; i<oInit.aaData.length ; i++ )
				{
					_fnAddData( oSettings, oInit.aaData[ i ] );
				}
			}
			else
			{
				/* Grab the data from the page */
				_fnGatherData( oSettings );
			}
			
			/* Copy the data index array */
			oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
			
			/* Calculate sizes for columns */
			if ( oSettings.oFeatures.bAutoWidth )
			{
				_fnCalculateColumnWidths( oSettings );
			}
			
			/* Initialisation complete - table can be drawn */
			oSettings.bInitialised = true;
			
			/* Check if we need to initialise the table (it might not have been handed off to the
			 * language processor)
			 */
			if ( bInitHandedOff === false )
			{
				_fnInitalise( oSettings );
			}
		});
	};
})(jQuery);


jQuery.fn.dataTableExt.oApi.fnSetFilteringDelay = function ( oSettings, iDelay ) {
	/*
	 * Type:        Plugin for DataTables (www.datatables.net) JQuery plugin.
	 * Name:        dataTableExt.oApi.fnSetFilteringDelay
	 * Version:     2.0.0
	 * Description: Enables filtration delay for keeping the browser more
	 *              responsive while searching for a longer keyword.
	 * Inputs:      object:oSettings - dataTables settings object
	 *              integer:iDelay - delay in miliseconds
	 * Returns:     JQuery
	 * Usage:       $('#example').dataTable().fnSetFilteringDelay(250);
	 *
	 * Author:      Zygimantas Berziunas (www.zygimantas.com) and Allan Jardine (v2)
	 * Created:     7/3/2009
	 * Language:    Javascript
	 * License:     GPL v2 or BSD 3 point style
	 * Contact:     zygimantas.berziunas /AT\ hotmail.com
	 */
	var _that = this;
	this.each( function ( i ) {
		$.fn.dataTableExt.iApiIndex = i;
		iDelay  = (iDelay && (/^[0-9]+$/.test(iDelay))) ? iDelay : 250;
		
		var $this = this, oTimerId;
		var anControl = $( 'input', _that.fnSettings().anFeatures.f );
		
		anControl.unbind( 'keyup' ).bind( 'keyup', function() {
			var $$this = $this;
			window.clearTimeout(oTimerId);
			
			oTimerId = window.setTimeout(function() {
				$.fn.dataTableExt.iApiIndex = i;
				_that.fnFilter( anControl.val() );
			}, iDelay);
		});
		
		return this;
	} );
	return this;
};


