unit ResultsForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.SysUtils,
  System.Variants,
  System.Classes,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.StdCtrls,
  Vcl.Grids;

type
  TFrmResults = class(TForm)
    LblTitle: TLabel;
    LblAramaId: TLabel;
    EdtAramaId: TEdit;
    BtnLoad: TButton;
    BtnClose: TButton;
    GridResults: TStringGrid;
    LblStatus: TLabel;
    procedure BtnLoadClick(Sender: TObject);
    procedure BtnCloseClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private
    procedure SetupGridColumns;
  public
    procedure SetDefaultAramaId(const AAramaId: Integer);
  end;

var
  FrmResults: TFrmResults;

implementation

{$R *.dfm}

uses
  UResultsService,
  UJwtTokenStore;

const
  COL_ID = 0;
  COL_NAME = 1;
  COL_INDUSTRY = 2;
  COL_CITY = 3;
  COL_ADDRESS = 4;
  COL_WEBSITE = 5;
  COL_PHONE = 6;
  COL_EMAIL = 7;
  COL_CONFIDENCE = 8;
  COL_OFFICIALS = 9;
  COL_SOURCE_URL = 10;
  COL_UPDATED_AT = 11;
  GRID_COL_COUNT = 12;

procedure TFrmResults.FormCreate(Sender: TObject);
begin
  SetupGridColumns;
end;

procedure TFrmResults.SetupGridColumns;
begin
  GridResults.ColCount := GRID_COL_COUNT;
  GridResults.FixedRows := 1;
  GridResults.RowCount := 1;

  GridResults.ColWidths[COL_ID] := 40;
  GridResults.ColWidths[COL_NAME] := 180;
  GridResults.ColWidths[COL_INDUSTRY] := 200;
  GridResults.ColWidths[COL_CITY] := 100;
  GridResults.ColWidths[COL_ADDRESS] := 220;
  GridResults.ColWidths[COL_WEBSITE] := 140;
  GridResults.ColWidths[COL_PHONE] := 110;
  GridResults.ColWidths[COL_EMAIL] := 160;
  GridResults.ColWidths[COL_CONFIDENCE] := 60;
  GridResults.ColWidths[COL_OFFICIALS] := 180;
  GridResults.ColWidths[COL_SOURCE_URL] := 200;
  GridResults.ColWidths[COL_UPDATED_AT] := 140;

  GridResults.Cells[COL_ID, 0] := 'ID';
  GridResults.Cells[COL_NAME, 0] := 'Firma Adı';
  GridResults.Cells[COL_INDUSTRY, 0] := 'Sektör';
  GridResults.Cells[COL_CITY, 0] := 'Şehir';
  GridResults.Cells[COL_ADDRESS, 0] := 'Adres';
  GridResults.Cells[COL_WEBSITE, 0] := 'Website';
  GridResults.Cells[COL_PHONE, 0] := 'Telefon';
  GridResults.Cells[COL_EMAIL, 0] := 'E-posta';
  GridResults.Cells[COL_CONFIDENCE, 0] := 'Güven';
  GridResults.Cells[COL_OFFICIALS, 0] := 'Yetkili(ler)';
  GridResults.Cells[COL_SOURCE_URL, 0] := 'Kaynak URL';
  GridResults.Cells[COL_UPDATED_AT, 0] := 'Son Güncelleme';
end;

procedure TFrmResults.BtnCloseClick(Sender: TObject);
begin
  Close;
end;

procedure TFrmResults.BtnLoadClick(Sender: TObject);
var
  LAramaId: Integer;
  LService: TResultsService;
  LData: TCompanyResults;
  I: Integer;
  LRow: Integer;
begin
  LAramaId := StrToIntDef(Trim(EdtAramaId.Text), -1);
  if LAramaId <= 0 then
    raise Exception.Create('Gecerli bir arama_id giriniz.');

  LblStatus.Caption := 'Results endpoint cagriliyor...';

  LService := TResultsService.Create;
  try
    LData := LService.GetCompanies(LAramaId, TJwtTokenStore.GetToken);

    // PERFORMANS: RowCount'u satir satir degil TEK SEFERDE toplam sayiya ayarla
    // (satir satir buyutmek O(n^2) yeniden tahsis yapar, 100+ sonucta yavaslar).
    GridResults.RowCount := Length(LData) + GridResults.FixedRows;

    GridResults.BeginUpdate;
    try
      for I := 0 to High(LData) do
      begin
        LRow := I + GridResults.FixedRows;
        GridResults.Cells[COL_ID, LRow] := IntToStr(LData[I].Id);
        GridResults.Cells[COL_NAME, LRow] := LData[I].Name;
        GridResults.Cells[COL_INDUSTRY, LRow] := LData[I].Industry;
        GridResults.Cells[COL_CITY, LRow] := LData[I].City;
        GridResults.Cells[COL_ADDRESS, LRow] := LData[I].Address;
        GridResults.Cells[COL_WEBSITE, LRow] := LData[I].Website;
        GridResults.Cells[COL_PHONE, LRow] := LData[I].Phone;
        GridResults.Cells[COL_EMAIL, LRow] := LData[I].Email;
        GridResults.Cells[COL_CONFIDENCE, LRow] := IntToStr(LData[I].ConfidenceScore);
        GridResults.Cells[COL_OFFICIALS, LRow] := LData[I].OfficialsSummary;
        GridResults.Cells[COL_SOURCE_URL, LRow] := LData[I].SourceUrl;
        GridResults.Cells[COL_UPDATED_AT, LRow] := LData[I].UpdatedAt;
      end;
    finally
      GridResults.EndUpdate;
    end;

    LblStatus.Caption := 'Toplam kayit: ' + IntToStr(Length(LData));
  finally
    LService.Free;
  end;
end;

procedure TFrmResults.SetDefaultAramaId(const AAramaId: Integer);
begin
  if AAramaId > 0 then
    EdtAramaId.Text := IntToStr(AAramaId)
  else
    EdtAramaId.Text := '';
end;

end.
