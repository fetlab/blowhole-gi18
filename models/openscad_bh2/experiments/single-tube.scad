/*
 * The radius of the sphere
 */
spRadius = 10;

/*
 * The number of faces of the solids. 100 is enough for a good print
 */
 quality = 100;
 
/*
 * The radius of the opening
 */
cyRadius = 2.5;
  
/*
 * The tube length
 */
cyLength = 7.5;

/* 
 * Distance between the sphere and the enclosure
 */
_dx = 4;

/*
 * 
 */
 _dz = 8;
 
/*
 * The text extrusion
 */
txExtrusion = 3;
 
/*
 * Wrapper for sphere
 */
module _sphere(sphereRadius, quality=50) {
    sphere(sphereRadius, center=true,$fn=quality);
}

/*
 * Wrapper for cylinder
 */
module _cylinder(cyRadius, cyLength, quality=50) {
    cylinder(r1=cyRadius,r2=cyRadius, h=cyLength, $fn=quality);
}

/*
 * Text identification for the enclosure.
 */
module txInfo() {
    linear_extrude(txExtrusion) {
        mirror([0,1,0]) {
            text(text=str(, "(ST)", spRadius, ",", cyLength),             halign="center", valign="center", size=3);
        }
    }
}

module enclosure(quality=50) {
    //     translate([0,0, spRadius + cyLength])
    translate([0,0, spRadius])
    mirror([0,0,1])
        cylinder(r1=spRadius + _dx, r2=spRadius + _dx, 
        h=spRadius * 2 + cyLength + _dz,
        $fn=quality);
}

module make() { 
    difference() {
        difference() { 
            enclosure();
            union() { 
                _sphere(spRadius, quality);
                translate([0, 0, spRadius - 1])
                    _cylinder(cyRadius, cyLength + 1, quality);
            }
        }
        translate([0, 0, -spRadius- cyLength - 1])
            txInfo();
    }
}

make();
