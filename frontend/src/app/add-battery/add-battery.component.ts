import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-add-battery',
  templateUrl: './add-battery.component.html',
  styleUrls: ['./add-battery.component.scss']
})
export class AddBatteryComponent implements OnInit {

  private formGroup: FormGroup;
  private nameOfAttributes;
  private url: String = "addBattery";
  private typeOfObject: String = "Battery";

  constructor(private _formBuilder: FormBuilder) {
    this.nameOfAttributes = {
      "batteryEfficiency": "Battery Efficiency (between 0 and 1)",
      "chargeUpperBound": "Charge Upper Bound in W",
      "dischargeUpperBound": "Discharge Upper Bound in W",
      "energyUpperBound": "Energy Upper Bound in Wh",
      "selfDischargingRate": "Self Discharging Rate in W"
    }    

    // init the formGroup
    this.formGroup = this._formBuilder.group({
      name: ['', Validators.required],
      lat: ['', Validators.required],
      long: ['', Validators.required],
      batteryEfficiency: ['', Validators.required],
      chargeUpperBound: ['', Validators.required],
      dischargeUpperBound: ['', Validators.required],
      energyUpperBound: ['', Validators.required],
      selfDischargingRate: ['', Validators.required]
    });
  }

  ngOnInit() {
  }
}

