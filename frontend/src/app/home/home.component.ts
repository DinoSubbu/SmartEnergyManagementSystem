import { Component, OnInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material';
import { HttpService } from '../services/http.service';
import {SelectionModel} from '@angular/cdk/collections';



@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  ngOnInit(): void {
  }

  displayedColumns: string[][] = [
    ["name", "lat", "long", "powerCoefficient", "area", "angleOfModule"],
    ["name", "lat", "long", "powerCoefficient", "radius"],
    ["name", "lat", "long"],
    ["name", "lat", "long", "batteryEfficiency", "energyUpperBound", "selfDischargingRate"],
  ];

  dataSource: any[] = [];
  selection = new SelectionModel(true, []);
s
  constructor(private snackbar: MatSnackBar, private http: HttpService) {
    let requestBuildings = this.http.makeGetRequest("getBuildings");
    let requestBatteries = this.http.makeGetRequest("getBatteries");
    let requestSolar = this.http.makeGetRequest("getSolar");
    let requestWind = this.http.makeGetRequest("getWind");
    this.requestObject(requestSolar, 0);
    this.requestObject(requestWind, 1);
    this.requestObject(requestBuildings, 2);
    this.requestObject(requestBatteries, 3);
    
    
  }

  requestObject(request, tableNumber: number) {
    request.subscribe(
      (data: any) => {
        // connection successfull, but empty array returned
        if (data.length == 0) {
          this.snackbar.open('Could not get data.', '', {
            duration: 2000
          });
          return;
        }
        console.log(data)

        this.dataSource[tableNumber] = new MatTableDataSource(data);

        this.snackbar.open('Data gathered.', '', {
          duration: 2000
        });



      },
      // error handling
      error => {
        console.log(error);
        this.snackbar.open('Could not get data.', '', {
          duration: 3000
        });

      });

  }




}
