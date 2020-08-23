import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-add-solar',
  templateUrl: './add-solar.component.html',
  styleUrls: ['./add-solar.component.scss']
})
export class AddSolarComponent implements OnInit {

  private formGroup: FormGroup;
  private nameOfAttributes;
  private url: String = "addSolar";
  private typeOfObject: String = "Solar Plant";

  constructor(private _formBuilder: FormBuilder) {
    this.nameOfAttributes = {
      "powerCoefficient": "Power Coefficient (between 0 and 1)",
      "area": "Area in m^2",
      "angleOfModule": "Angle of Module in °"
    }    

    // init the formGroup
    this.formGroup = this._formBuilder.group({
      name: ['', Validators.required],
      lat: ['', Validators.required],
      long: ['', Validators.required],
      powerCoefficient: ['', Validators.required],
      area: ['', Validators.required],
      angleOfModule: ['', Validators.required]
    });
  }

  ngOnInit() {
  }
}
