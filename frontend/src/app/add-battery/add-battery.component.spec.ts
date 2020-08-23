import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddBatteryComponent } from './add-battery.component';

describe('AddBatteryComponent', () => {
  let component: AddBatteryComponent;
  let fixture: ComponentFixture<AddBatteryComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddBatteryComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddBatteryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
