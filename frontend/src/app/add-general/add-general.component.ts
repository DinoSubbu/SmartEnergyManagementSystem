import { Component, OnInit, Input } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpService } from '../services/http.service';
import { MatSnackBar, MatTableDataSource } from '@angular/material';
import { tileLayer, latLng } from 'leaflet';
import { timeout } from 'q';
import { BuildingComponent } from '../add-building/add-building.component';
import { Router } from '@angular/router';

declare let L: any;



@Component({
  selector: 'app-add-general',
  templateUrl: './add-general.component.html',
  styleUrls: ['./add-general.component.scss']
})
export class AddGeneralComponent implements OnInit {
  @Input() nameOfAttributes: { String: string };
  @Input() formGroup: FormGroup;
  @Input() typeOfObject: string;
  @Input() url: string;

  // map values
  private map: any;
  private currentMarker: any;
  private updateValuesFromMap: boolean = false;

  // component values
  private displayedColumns: string[] = ["name", "est", "let", "e", "lot"];
  private components: BuildingComponent[] = [];
  private dataSource = new MatTableDataSource();
  private componentName: string;
  private componentEst: number;
  private componentLet: number;
  private componentE: number;
  private componentLot: number;

  // chart attributes for demand profile
  private buildingType: string = "household";
  private household: number[] = [
    332.1709,
    262.819,
    234.3779,
    229.2816,
    235.4617,
    255.1405,
    283.4671,
    432.1225,
    534.3769,
    559.6205,
    608.4645,
    585.9718,
    648.3234,
    668.8364,
    557.5756,
    526.7263,
    550.5535,
    529.8151,
    641.3157,
    754.156,
    782.5452,
    740.9206,
    597.4084,
    475.6613
  ];
  private usedData: number[];
  private valueToChange: number;
  private office: number[] = [
    3295.45431,
    3230.50214,
    3088.39031,
    3066.93376,
    3029.34311,
    3013.018,
    2898.94943,
    2892.45014,
    3028.16952,
    3606.25,
    4247.32906,
    6434.29533,
    5214.87252,
    5814.52432,
    5659.70644,
    5093.25284,
    5255.44979,
    5019.69489,
    4628.43443,
    4269.22425,
    4071.98214,
    3855.55357,
    3606.15708,
    3414.28935
  ];
  private changeChartColumn: number = 0;
  public chartType: string = 'bar';
  public chartDatasets: Array<any> = [];
  public chartLabels: Array<any> = [];
  public chartColors: Array<any> = [
    {
      backgroundColor: 'rgba(83, 109, 254, .2)',
      borderColor: 'rgba(83, 109, 254, .7)',
      borderWidth: 2,
    }
  ];
  public chartOptions: any = {
    responsive: true,
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  };

  constructor(private snackBar: MatSnackBar, private _formBuilder: FormBuilder, private http: HttpService, private router: Router) {
    let chartLabelsTemp: string[] = [];
    for (let i = 0; i < 24; i++) {
      chartLabelsTemp.push(i.toString());
    }
    this.chartLabels = chartLabelsTemp;
    this.usedData = this.household;
    this.changeGraphData();

  }

  ngOnInit() {

  }

  onChanges() {
    // if user manually changes lat and long the marker on the map will also be resetted
    this.formGroup.get("lat").valueChanges.subscribe(val => {
      if (!this.updateValuesFromMap) {
        let point = [this.formGroup.value["lat"], this.formGroup.value["long"]]
        this.map.panTo(point)
        this.changeMarker(point)
      }

    });
    this.formGroup.get("long").valueChanges.subscribe(val => {
      if (!this.updateValuesFromMap) {
        let point = [this.formGroup.value["lat"], this.formGroup.value["long"]]
        this.map.panTo(point)
        this.changeMarker(point)
      }
    });
  }

  changeMarker(point) {
    if (this.currentMarker != null) {
      this.map.removeLayer(this.currentMarker);
    }
    this.currentMarker = L.marker(point).addTo(this.map)
  }

  ngAfterViewInit(): void {
    // map initialization 

    this.map = L.map('map').setView([48.78232, 9.17702], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    this.map.on("click", this.onMapClick.bind(this));
    this.onChanges();


  }

  onMapClick(e) {
    this.updateValuesFromMap = true;
    this.formGroup.patchValue({ "lat": e.latlng.lat, "long": e.latlng.lng });
    this.changeMarker(e.latlng)
    this.updateValuesFromMap = false;
  }


  addPanel() {
    let panel = {}
    for (let key in this.formGroup.value) {
      // special cases 
      if (key == "name" || key == "lat" || key == "long") {
        panel[key] = this.formGroup.value[key];

      } else if (key == "components") {
        panel[key] = this.components;

      } else if (key == "historicalData") {
        panel[key] = this.usedData;

      } else {
        panel[key] = parseFloat(this.formGroup.value[key]);
      }

    }

    let request = this.http.makePostRequest(this.url, JSON.stringify(panel));
    request.subscribe(
      (data: any) => {
        this.snackBar.open('Added ' + this.typeOfObject + '.', '', {
          duration: 3000
        });
        console.log(data);
        this.router.navigateByUrl('entities');
      },
      // error handling
      error => {
        if (error.status == 409) {
          this.snackBar.open('Conflict with the given attributes.', '', {
            duration: 3000
          });
        } else {
          console.log(error);
          this.snackBar.open('Could not add ' + this.typeOfObject + '.', '', {
            duration: 3000
          });
        }

      });

  }

  // functions related to components of buildings
  addComponent() {

    let component: BuildingComponent = {
      name: this.componentName,
      est: this.componentEst,
      let: this.componentLet,
      e: this.componentE,
      lot: this.componentLot,
    }
    this.components.push(component);
    this.dataSource = new MatTableDataSource(this.components);
    console.log(this.components)
  }

  changeGraphData() {
    this.chartDatasets = [{ data: this.usedData, label: "Demand Profile" }];
  }

  changeBuildingType(value) {
    if (value == "household") {
      this.usedData = this.household;
      this.changeGraphData();

    }
    if (value == "office") {
      this.usedData = this.office;
      this.changeGraphData();
    }
  }

  changeValueForBar() {
    this.usedData[this.changeChartColumn] = this.valueToChange;
    this.changeGraphData()

  }

  public chartClicked(e: any): void {
    this.changeChartColumn = e.active["0"]._index;
    console.log(e.active["0"]._index)
  }
  public chartHovered(e: any): void {
  }
}

