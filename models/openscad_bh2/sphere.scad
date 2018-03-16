
/*
 * X-axis distance between the sphere and the surrounding cylinder
 */
_dx=4;

/*
 * Y-axis Distance between the bottom of the cylinder and the sphere
 */
_bottom = 10;

/*
 * The radius of the sphere
 */
spRadius = 4.6;

/*
 * The tube length
 */
cyHeight = 3;

/*
 * The opening radius
 */
cyRadius = 2.5;

/*
 * Height of the text extrusion
 */
txExtrusion = 3;


module enclosure(sR, cH, quality=50) {
    translate([0, 0, -sR- _bottom]) {
        cylinder(r=sR+_dx, h=sR+cH+sR+_bottom, center=false, $fn=quality);
    }
}

module cavity(sR, cR, cH, quality=50) {
    translate([0, 0, spRadius - 0.8]) {
        cylinder(h=cH+0.8,r=cR, $fn=quality);
    }
    sphere(r=sR, $fn=quality);
}


module txInfo() {
    linear_extrude(txExtrusion) {
        mirror([0,1,0]) {
            text(   text=str("8"), halign="center",
                    valign="center", size=8);
        }
    }
}

module make() {
    difference() {
        difference() {
            enclosure(spRadius, cyHeight, 100);
            cavity(spRadius, cyRadius, cyHeight, 100);
        }
        translate([0, 0,  - spRadius - _bottom])
            txInfo();
    }
}

make(); 