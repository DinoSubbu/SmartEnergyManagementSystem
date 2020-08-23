import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-add-wind-turbine',
  templateUrl: './add-wind-turbine.component.html',
  styleUrls: ['./add-wind-turbine.component.scss']
})
export class AddWindTurbineComponent implements OnInit {

  private formGroup: FormGroup;
  private nameOfAttributes;
  private url: String = "addWindTurbine";
  private typeOfObject: String = "Wind Turbine";

  constructor(private _formBuilder: FormBuilder) {
    this.nameOfAttributes = {
      "powerCoefficient": "Power Coefficient (between 0 and 1)",
      "radius": "Radius in m"
    }    

    // init the formGroup
    this.formGroup = this._formBuilder.group({
      name: ['', Validators.required],
      lat: ['', Validators.required],
      long: ['', Validators.required],
      powerCoefficient: ['', Validators.required],
      radius: ['', Validators.required]      
    });
  }

  ngOnInit() {
  }
}

