function PeriodicPlayer(player) 
{ 
  this.player = player;    
  this.currentStopListener = null;

  this.setPeriod = function(start,end) 
  {
    player.pause();
    if(this.currentStopListener != null) {
      this.player.media.removeEventListener("timeupdate", this.currentStopListener, false);
    }
    
    this.currentStopListener = function(event) {
     if (player.node.currentTime > end) {
          player.setCurrentTime(start);
          player.pause();
      }
    };
    
    player.media.addEventListener("timeupdate", this.currentStopListener, false);
    player.setCurrentTime(start);
  }
}

var playerGlobal;
$( document ).ready(function() {
  $('#player').mediaelementplayer({
    stretching: 'responsive',
    success: function(media, node, player) {
      $('#' + node.id + '-mode').html('mode: ' + player.pluginType);
      
      media.addEventListener('loadedmetadata', function() {
        playerGlobal = new PeriodicPlayer(player);
      });
    }
    //, youtube:{ nocookie: true }
  });
});


var app = angular.module('test', ['schemaForm']);

app.controller('MainController', function($rootScope, $scope, $compile) {
  $scope.logs = {};

  $scope.selected = null;

  var url = new URL(window.location.href);
  $scope.widget = { title: url.searchParams.get("name") !== null ? url.searchParams.get("name") : 'New' };

  
  $scope.addLogfileToModel = function(id, data) {
    $scope.logs[id] = data; //push({"id":id, "data":data});
  };
  
  $scope.addPeriod = function(timeline, interval_id, log_offset, video_offset) {
    var model = $scope.logs[timeline.attr('id')];
    var interval = model.intervals[interval_id];
    var offset = video_offset - log_offset;
    var width = (interval.end - interval.begin) / (model.end - log_offset) * 100;
    var starting_at = (interval.begin - log_offset) / (model.end - log_offset) * 100;

    var str = '<a href="#" id="'+interval_id+'" class="button '+interval.type+'" data-toggle="tooltip" title="'+interval.type+'"></a>';
    var o = $compile(str)($scope);
    $(o).css( "width", width + "%");
    $(o).css( "left", starting_at + "%");

    o[0].onclick = function(i,e) {
      $rootScope.$broadcast('setPeriod', $(this).parent().attr('id'), interval_id, offset);
      o.addClass("selected");
      
      if($scope.selected != null) {
        $scope.selected.removeClass("selected");
      }
      $scope.selected = o;
    };
    
    timeline.append(o);
  };
  
  $scope.save = function(event) {
      var name = $scope.widget.title.trim();
        if(name.length === 0 || name.toLowerCase() === 'new') {
            showSavingAlert('<b>WARNING: you need to set a tag!</b>', 'alert alert-warning', 1000, true);
            return;
        }

        var url = new URL(window.location.href);
        var game = url.searchParams.get("game");
        if (game === null) {
            showSavingAlert('<b>ERROR: invalid game id!</b>', 'alert alert-danger', 0, false);
            return;
        }

        data = [];
        for(var i in $scope.logs) {
            // check & remove empty objects/arrays
            var lbl = $scope.logs[i].labels;
            for(var l in lbl) {
                for(var a in lbl[l]) {
                    if ($.isEmptyObject(lbl[l][a])) { delete lbl[l][a]; }
                }
                if ($.isEmptyObject(lbl[l])) { delete lbl[l]; }
            }
            if ($.isEmptyObject(lbl)) { continue; }
            // add to the sending array
            data.push({'id': i, 'labels': JSON.stringify($scope.logs[i].labels, null, '  ')});
        }

        if(data.length > 0) {
          $.post(null, {"tag" : $scope.widget.title, "data" : data})
            .done(function( result ) {
              if (result === 'SUCCESS') {
                showSavingAlert('<b>Saved!</b>', 'alert alert-success', 800, true);
              } else {
                showSavingAlert('<b>'+result+'</b>', 'alert alert-danger', 0, false);
              }
            });
        } else {
          showSavingAlert('<b>Nothing to save!</b>', 'alert alert-warning', 600, true);
        }
  };
});


app.controller('FormController', function($scope) {
  labels = typeof ANNOTATION_LABELS === 'undefined' ? {} : ANNOTATION_LABELS;
  var properties = {};
  var form = [];
  
  for(var key in labels) {
    var p = labels[key];
    properties[key] = {
      "type": "array", 
      "title": p.title,
      "items": {"type": "string", "enum": p.labels.map(i => i.value)}
    };
    form.push({
      "key": key,
      "type": "checkboxes",
      "titleMap": p.labels
    });
  }
  
  properties["comment"] = {"type": "string", "title": "Comment"};
  form.push({
      "key": "comment",
      "type": "textarea",
      "placeholder": "Make a comment"
    });
  
  
  $scope.schema = {
    "type" : "object", 
    "properties": properties
  };
  
  $scope.form = form;

  $scope.model = {};

  $scope.$on('setPeriod', function(event, log_id, interval_id, offset) {
      if(typeof $scope.logs[log_id].labels[interval_id] === 'undefined') { $scope.logs[log_id].labels[interval_id] = {}; }
      $scope.model = $scope.logs[log_id].labels[interval_id];
      $scope.$apply();
  });
});


app.controller('PlayerController', function($scope) {
    // add video sources to source selector
    var sourceSelect = $('#video_configuration_source');
    $('#player').children().each(function (i,s) {
        sourceSelect.append('<option value="'+this.src+'">'+(this.type?this.type:mejs.Utils.getTypeFromFile(this.src))+'</option>');
    });
    // switch source listener
    sourceSelect.change(function (e) {
        playerGlobal.player.setSrc(this.value);
        playerGlobal.player.setPoster('');
        playerGlobal.player.load();
    });

    $scope.$on('setPeriod', function(event, log_id, interval_id, offset) {
        var t_begin = $scope.logs[log_id].intervals[interval_id].begin + offset - $('#video_configuration_before').val();
        var t_end = $scope.logs[log_id].intervals[interval_id].end + offset + $('#video_configuration_after').val();
        playerGlobal.setPeriod(t_begin, t_end);
    });
});

app.controller('DrawingController', function($scope) {
    $scope.$on('setPeriod', function(event, log_id, interval_id, offset) {
        //draw the robot position
        draw(
            $scope.logs[log_id].intervals[interval_id].pose.x/10.0,
            $scope.logs[log_id].intervals[interval_id].pose.y/10.0,
            $scope.logs[log_id].intervals[interval_id].pose.r,
            $scope.logs[log_id].intervals[interval_id].ball.x/10.0,
            $scope.logs[log_id].intervals[interval_id].ball.y/10.0
        );
    });
});

app.directive('timeline', function($compile) {
    return {
        //restrict: 'AE',
        //replace: true,
        //template: '<div class="timeline"></div>',
        link: function(scope, element, attrs) {
            $.getJSON( attrs.file, function( data ) {
                // if not already available, add the label container
                if(typeof data.labels === 'undefined') { data.labels = {}; }
                if(typeof data.sync === 'undefined') { data.sync = {}; }
                // load labels
                if(typeof attrs.labels !== 'undefined') {
                    $.getJSON( attrs.labels, function( labels ) {
                        $.extend(data.labels, labels);
                    });
                }
                scope.addLogfileToModel(attrs.id, data);
                // show the player number in the timeline
                element.append('<div class="info">#'+attrs.playernumber+'</div>');
                // iterate through the actions and add the interval to the timeline
                for(var interval_id in data.intervals) {
                    var v = data.intervals[interval_id];
                    // collect all found actions in the log file and add a control to the UI
                    if($('#event_configuration input[name="'+v.type+'"]').length === 0) {
                        var event_checkbox = $('<div class="col-xs-3"><div class="checkbox"><label><input type="checkbox" name="'+v.type+'" checked> '+v.type+'</label></div></div>');
                        event_checkbox.change(function(e) { hide_event(e.target.name) });
                        $('#event_configuration .row').append(event_checkbox);
                    }
                    scope.addPeriod(element, interval_id, attrs.logoffset, attrs.videooffset);
                }
            });
        }
    };
});

function hide_event(e) {
  $("."+e).toggleClass('visibility_hidden');
}

function showSavingAlert(content, clz, delay, fadeout) {
  var alert = $("#label_title_form .alert");
  alert.html(content).attr('class', clz).fadeIn();
  if (fadeout) {
    alert.delay(delay).fadeOut();
  }
}

// initialize the alert
$("#label_title_form .alert").hide();
$("#label_title_form .alert").removeClass('hidden');

// update/show the current open state of the configuration panel
$('#configuration .panel-collapse').on('show.bs.collapse', function () {
  $('#configuration_control a[href="#'+this.id+'"] .glyphicon').toggleClass('glyphicon-plus glyphicon-minus');
}).on('hide.bs.collapse', function () {
  $('#configuration_control a[href="#'+this.id+'"] .glyphicon').toggleClass('glyphicon-plus glyphicon-minus');
});