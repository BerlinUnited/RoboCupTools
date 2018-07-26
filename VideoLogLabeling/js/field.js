function drawField(ctx, width, height)
{
  var xOwnGround = 900;
  var xOppGround = 70;
  var yRightBorder = 600;
  var yLeftBorder = 70;

  var goalPostRadius = 5;
  var borderStripWidth = 70;
  var lineWidth = 5;
  
  ctx.beginPath();
  ctx.rect(0,0,740,1040);
  ctx.fillStyle = '#00AA00';
  ctx.fill();
  //Field Borders      
  ctx.rect(yLeftBorder,xOppGround,yRightBorder,xOwnGround)
  ctx.lineWidth = lineWidth;
  ctx.strokeStyle = 'white';
  ctx.stroke();

  //Center Line
  ctx.beginPath();
  ctx.moveTo(yLeftBorder, height/2);
  ctx.lineTo(740-borderStripWidth, height/2);
  ctx.stroke();
  //Opp Penalty  Mark
  ctx.translate((width/2),(height/2));
  ctx.beginPath();
  ctx.arc(0, -130, 5, 0, 2 * Math.PI, false);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.stroke();
  //Own Penalty  Mark
  ctx.beginPath();
  ctx.arc(0, 130, 5, 0, 2 * Math.PI, false);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.stroke();
  //Circle
  ctx.beginPath();
  ctx.arc(0, 0, borderStripWidth, 0, 2 * Math.PI, false);
  ctx.stroke();
  //Own Goal Posts
  ctx.beginPath();
  ctx.arc(75, 450, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(-75, 450, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  
  //Own Goal
  ctx.fillStyle = '#99AAFF';
  ctx.fillRect(-75, 450, 150, 50);
  
  ctx.beginPath();
  ctx.moveTo(75, 450);
  ctx.lineTo(75, 450+50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-75, 450);
  ctx.lineTo(-75, 450+50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-75, 450+50);
  ctx.lineTo(75, 450+50);
  ctx.stroke();
  //Opp Goal Posts
  ctx.beginPath();
  ctx.arc(75, -450, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(-75, -450, goalPostRadius, 0, 2 * Math.PI, false);
  ctx.stroke();
  
  //Opp Goal
  ctx.fillStyle = '#FFAA99';
  ctx.fillRect(-75, -450, 150, -50);
  
  ctx.beginPath();
  ctx.moveTo(75, -450);
  ctx.lineTo(75, -450-50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-75, -450);
  ctx.lineTo(-75, -450-50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-75, -450-50);
  ctx.lineTo(75, -450-50);
  ctx.stroke();

  //Own Penalty Area
  ctx.beginPath();
  ctx.moveTo(110, 450);
  ctx.lineTo(110, 450-50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-110, 450);
  ctx.lineTo(-110, 450-50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-110, 450-50);
  ctx.lineTo(110, 450-50);
  ctx.stroke();

  //Opp Penalty Area
  ctx.beginPath();
  ctx.moveTo(110, -450);
  ctx.lineTo(110, -450+50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-110, -450);
  ctx.lineTo(-110, -450+50);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-110, -450+50);
  ctx.lineTo(110, -450+50);
  ctx.stroke();

  ctx.translate(-(width/2),-(height/2));
}

function drawRobot(ctx, width, height,x,y,rot)
{
  var image = document.getElementById("nao");
  
  //Draw Robot: Image-length: 557, Image-height = 865
  ctx.translate(x, y);
  ctx.rotate(rot);
  
  var scale = 0.07;
  ctx.scale(scale, scale);
  ctx.translate(-279, -433);
  ctx.drawImage(image, 0, 0);
  ctx.translate(279, 433);
  ctx.scale(1.0/scale, 1.0/scale);
  
  ctx.rotate(-rot);
  ctx.translate(-x, -y);
}

function drawBall(ctx, width, height,x,y) 
{
  ctx.translate(x, y);
  ctx.beginPath();
  ctx.arc(0, 0, 7, 0, 2 * Math.PI, false);
  ctx.fillStyle = '#FFAA99';
  ctx.fill();
  ctx.translate(-x, -y);
}

function draw(x,y,rot, bx, by)
{
  var canvas = document.getElementById('canvas');
  if (canvas.getContext)
  {
    var width = canvas.width;
    var height = canvas.height;

    //var image = document.getElementById("nao");

    var ctx = canvas.getContext('2d');
    //ctx.restore();
    //ctx.save();
    
      drawField(ctx, width, height);
      
      // global field transform
      
      ctx.translate((width/2),(height/2));
      ctx.rotate(-Math.PI/2.0);
      ctx.scale(1, -1);
  
      drawRobot(ctx, width, height, x,y,rot);
      drawBall(ctx, width, height, bx,by);
      
      ctx.scale(1, -1);
      ctx.rotate(Math.PI/2.0);
      ctx.translate(-(width/2),-(height/2));

  }//end if  
}//end draw

/*
// jquery version
$( document ).ready(function() {
  draw(0,100,0.1, 100, 200);
});
*/
document.addEventListener('DOMContentLoaded', function () {
  draw(0,100,0.1, 100, 200);
});