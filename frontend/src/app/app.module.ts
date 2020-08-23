import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { HttpClientModule } from '@angular/common/http';

// angular material
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatButtonModule, MatInputModule, MatNativeDateModule, MatPaginator, MatPaginatorModule} from '@angular/material';
import {MatStepperModule} from '@angular/material/stepper';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatDividerModule} from '@angular/material/divider';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatListModule} from '@angular/material/list';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatSelectModule} from '@angular/material/select';
import {MatTableModule} from '@angular/material/table';
import {MatDatepickerModule} from '@angular/material/datepicker';
import { MatGridListModule } from '@angular/material/grid-list';
import {MatCheckboxModule} from '@angular/material/checkbox';

import { MDBBootstrapModule } from 'angular-bootstrap-md';

import { MapComponent } from './map/map.component';
import { HomeComponent } from './home/home.component';
import { DayAheadPricesComponent } from './day-ahead-prices/day-ahead-prices.component';
import { BatteryComponent } from './battery/battery.component';
import { EnergyGenerationComponent } from './energy-generation/energy-generation.component';
import { ScheduleComponent } from './schedule/schedule.component';
import { registerLocaleData } from '@angular/common';
import localeDe from '@angular/common/locales/de';
import { AddGeneralComponent } from './add-general/add-general.component';
import { AddWindTurbineComponent } from './add-wind-turbine/add-wind-turbine.component';
import { AddSolarComponent } from './add-solar/add-solar.component';
import { AddBatteryComponent } from './add-battery/add-battery.component';
import { AddBuildingComponent } from './add-building/add-building.component';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import { ComponentsComponent } from './components/components.component';
import { SettingsComponent } from './settings/settings.component';
import { BatteryForecastComponent } from './battery-forecast/battery-forecast.component';
import { CurrentGenerationComponent } from './current-generation/current-generation.component';
import { DemandComponent } from './demand/demand.component';
import { CurrentComponent } from './current/current.component';
import { ScheduleVariationComponent } from './schedule-variation/schedule-variation.component';
import { Co2ForecastProxyComponent } from './co2-forecast-proxy/co2-forecast-proxy.component';
import { GasBoilerComponent } from './gas-boiler/gas-boiler.component';

registerLocaleData(localeDe, 'de-DE');

@NgModule({
  declarations: [
    AppComponent,
    MapComponent,
    HomeComponent,
    DayAheadPricesComponent,
    BatteryComponent,
    EnergyGenerationComponent,
    ScheduleComponent,
    AddGeneralComponent,
    AddWindTurbineComponent,
    AddSolarComponent,
    AddBatteryComponent,
    AddBuildingComponent,
    ComponentsComponent,
    SettingsComponent,
    BatteryForecastComponent,
    CurrentGenerationComponent,
    DemandComponent,
    CurrentComponent,
    ScheduleVariationComponent,
    Co2ForecastProxyComponent,
    GasBoilerComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    MatIconModule,
    BrowserAnimationsModule,
    MatButtonModule,
    MatStepperModule,
    MatFormFieldModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    MatSidenavModule,
    MatDividerModule,
    MatToolbarModule,
    MatListModule,
    MatSnackBarModule,
    MatSelectModule,
    MDBBootstrapModule.forRoot(),
    LeafletModule.forRoot(),
    MatProgressBarModule,
    MatTableModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatGridListModule,
    MatPaginatorModule,
    MatCheckboxModule

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
