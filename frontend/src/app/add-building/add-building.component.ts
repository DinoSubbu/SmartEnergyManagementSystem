import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

export interface BuildingComponent {
  name: string;
  est: number;
  let: number;
  e: number;
  lot: number;
}


@Component({
  selector: 'app-add-building',
  templateUrl: './add-building.component.html',
  styleUrls: ['./add-building.component.scss']
})
export class AddBuildingComponent implements OnInit {

  private formGroup: FormGroup;
  private nameOfAttributes;
  private url: String = "addBuilding";
  private typeOfObject: String = "Building";

  constructor(private _formBuilder: FormBuilder) {
    this.nameOfAttributes = {
      "historicalData": "Demand Profile",
      "components": "Components"
    }    

    // init the formGroup
    this.formGroup = this._formBuilder.group({
      name: ['', Validators.required],
      lat: ['', Validators.required],
      long: ['', Validators.required],
      historicalData: ['', Validators.required],
      components: ['', Validators.required]      
    });
  }

  ngOnInit() {
  }
}
