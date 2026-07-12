unit AdminForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.Rtti,
  System.SysUtils,
  System.Variants,
  System.Classes,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.StdCtrls,
  Vcl.ExtCtrls,
  Vcl.Grids,
  UAdminService;

type
  TAdminForm = class(TForm)
    LblTitle: TLabel;
    PnlLeft: TPanel;
    PnlRight: TPanel;
    PnlHistory: TPanel;
    PnlCompanies: TPanel;
    SplitterMain: TSplitter;
    SplitterRight: TSplitter;
    LblUsers: TLabel;
    LblHistory: TLabel;
    LblCompanies: TLabel;
    GridUsers: TStringGrid;
    GridSearchHistory: TStringGrid;
    GridCompanies: TStringGrid;
  private
    FUsersLoaded: Boolean;
    FLastSelectedUserId: Integer;
    procedure ConfigureUsersGrid;
    procedure ConfigureSearchHistoryGrid;
    procedure LoadUsers;
    procedure FillUsersGrid(const AUsers: TAdminUserItems);
    procedure LoadUserSearchHistory(const AUserId: Integer);
    procedure FillSearchHistoryGridFromValue(const AValue: TValue);
    function TryGetRecordFieldValue(const AItem: TValue; const AFieldNames: array of string; out AValue: TValue): Boolean;
    procedure GridUsersSelectCell(Sender: TObject; ACol, ARow: Integer; var CanSelect: Boolean);
  protected
    procedure DoShow; override;
  public
  end;

  TFrmAdmin = TAdminForm;

var
  FrmAdmin: TAdminForm;

implementation

{$R *.dfm}

uses
  UJwtTokenStore;

procedure TAdminForm.ConfigureUsersGrid;
begin
  GridUsers.FixedRows := 1;
  GridUsers.FixedCols := 0;
  GridUsers.ColCount := 5;
  GridUsers.RowCount := 2;

  GridUsers.Cells[0, 0] := 'ID';
  GridUsers.Cells[1, 0] := 'Username';
  GridUsers.Cells[2, 0] := 'Email';
  GridUsers.Cells[3, 0] := 'IsAdmin';
  GridUsers.Cells[4, 0] := 'CreatedAt';
  GridUsers.OnSelectCell := GridUsersSelectCell;
end;

procedure TAdminForm.ConfigureSearchHistoryGrid;
begin
  GridSearchHistory.FixedRows := 1;
  GridSearchHistory.FixedCols := 0;
  GridSearchHistory.ColCount := 5;
  GridSearchHistory.RowCount := 2;

  GridSearchHistory.Cells[0, 0] := 'SearchHistoryId';
  GridSearchHistory.Cells[1, 0] := 'Query';
  GridSearchHistory.Cells[2, 0] := 'Status';
  GridSearchHistory.Cells[3, 0] := 'CompanyCount';
  GridSearchHistory.Cells[4, 0] := 'CreatedAt';
end;

procedure TAdminForm.DoShow;
begin
  inherited;

  if FUsersLoaded then
    Exit;

  FLastSelectedUserId := -1;
  ConfigureUsersGrid;
  ConfigureSearchHistoryGrid;
  LoadUsers;
  FUsersLoaded := True;
end;

procedure TAdminForm.FillUsersGrid(const AUsers: TAdminUserItems);
var
  I: Integer;
  LAdminText: string;
begin
  if Length(AUsers) = 0 then
  begin
    GridUsers.RowCount := 2;
    Exit;
  end;

  GridUsers.RowCount := Length(AUsers) + 1;
  for I := 0 to High(AUsers) do
  begin
    if AUsers[I].IsAdmin then
      LAdminText := 'true'
    else
      LAdminText := 'false';

    GridUsers.Cells[0, I + 1] := IntToStr(AUsers[I].Id);
    GridUsers.Cells[1, I + 1] := AUsers[I].Username;
    GridUsers.Cells[2, I + 1] := AUsers[I].Email;
    GridUsers.Cells[3, I + 1] := LAdminText;
    GridUsers.Cells[4, I + 1] := AUsers[I].CreatedAt;
  end;
end;

procedure TAdminForm.FillSearchHistoryGridFromValue(const AValue: TValue);
var
  I: Integer;
  LItem: TValue;
  LFieldValue: TValue;
begin
  GridSearchHistory.RowCount := 2;

  if AValue.IsEmpty or (AValue.Kind <> tkDynArray) then
    Exit;

  if AValue.GetArrayLength = 0 then
    Exit;

  GridSearchHistory.RowCount := AValue.GetArrayLength + 1;
  for I := 0 to AValue.GetArrayLength - 1 do
  begin
    LItem := AValue.GetArrayElement(I);

    if TryGetRecordFieldValue(LItem, ['SearchHistoryId', 'Id', 'search_history_id'], LFieldValue) then
      GridSearchHistory.Cells[0, I + 1] := LFieldValue.ToString
    else
      GridSearchHistory.Cells[0, I + 1] := '';

    if TryGetRecordFieldValue(LItem, ['Query', 'query'], LFieldValue) then
      GridSearchHistory.Cells[1, I + 1] := LFieldValue.ToString
    else
      GridSearchHistory.Cells[1, I + 1] := '';

    if TryGetRecordFieldValue(LItem, ['Status', 'status'], LFieldValue) then
      GridSearchHistory.Cells[2, I + 1] := LFieldValue.ToString
    else
      GridSearchHistory.Cells[2, I + 1] := '';

    if TryGetRecordFieldValue(LItem, ['CompanyCount', 'company_count'], LFieldValue) then
      GridSearchHistory.Cells[3, I + 1] := LFieldValue.ToString
    else
      GridSearchHistory.Cells[3, I + 1] := '';

    if TryGetRecordFieldValue(LItem, ['CreatedAt', 'created_at'], LFieldValue) then
      GridSearchHistory.Cells[4, I + 1] := LFieldValue.ToString
    else
      GridSearchHistory.Cells[4, I + 1] := '';
  end;
end;

procedure TAdminForm.LoadUsers;
var
  LService: TAdminService;
  LUsers: TAdminUserItems;
begin
  LService := TAdminService.Create;
  try
    LUsers := LService.GetUsers(TJwtTokenStore.GetToken);
    FillUsersGrid(LUsers);
  finally
    LService.Free;
  end;
end;

procedure TAdminForm.LoadUserSearchHistory(const AUserId: Integer);
var
  LService: TAdminService;
  LMethod: TRttiMethod;
  LContext: TRttiContext;
  LType: TRttiType;
  LResult: TValue;
begin
  LService := TAdminService.Create;
  try
    LType := LContext.GetType(LService.ClassType);
    LMethod := LType.GetMethod('GetUserSearchHistory');
    if not Assigned(LMethod) then
      raise Exception.Create('GetUserSearchHistory fonksiyonu bulunamadi.');

    LResult := LMethod.Invoke(LService, [AUserId]);
    FillSearchHistoryGridFromValue(LResult);
  finally
    LService.Free;
  end;
end;

function TAdminForm.TryGetRecordFieldValue(const AItem: TValue; const AFieldNames: array of string; out AValue: TValue): Boolean;
var
  LContext: TRttiContext;
  LType: TRttiType;
  LField: TRttiField;
  LName: string;
begin
  Result := False;
  AValue := TValue.Empty;

  if AItem.IsEmpty then
    Exit;

  LType := LContext.GetType(AItem.TypeInfo);
  if not Assigned(LType) then
    Exit;

  for LName in AFieldNames do
  begin
    LField := LType.GetField(LName);
    if Assigned(LField) then
    begin
      AValue := LField.GetValue(AItem.GetReferenceToRawData);
      Exit(True);
    end;
  end;
end;

procedure TAdminForm.GridUsersSelectCell(Sender: TObject; ACol, ARow: Integer; var CanSelect: Boolean);
var
  LUserId: Integer;
begin
  if ARow < 1 then
    Exit;

  LUserId := StrToIntDef(Trim(GridUsers.Cells[0, ARow]), 0);
  if LUserId <= 0 then
    Exit;

  if LUserId = FLastSelectedUserId then
    Exit;

  LoadUserSearchHistory(LUserId);
  FLastSelectedUserId := LUserId;
end;

end.
