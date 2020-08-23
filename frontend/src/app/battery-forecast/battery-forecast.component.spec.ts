import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BatteryForecastComponent } from './battery-forecast.component';

describe('BatteryForecastComponent', () => {
  let component: BatteryForecastComponent;
  let fixture: ComponentFixture<BatteryForecastComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BatteryForecastComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BatteryForecastComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
