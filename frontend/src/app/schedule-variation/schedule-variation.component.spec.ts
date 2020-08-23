import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScheduleVariationComponent } from './schedule-variation.component';

describe('ScheduleVariationComponent', () => {
  let component: ScheduleVariationComponent;
  let fixture: ComponentFixture<ScheduleVariationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScheduleVariationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScheduleVariationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
