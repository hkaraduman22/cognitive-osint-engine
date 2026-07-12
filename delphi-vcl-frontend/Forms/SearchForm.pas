unit SearchForm;

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
  Vcl.StdCtrls;

type
  TFrmSearch = class(TForm)
    LblTitle: TLabel;
    LblQuery: TLabel;
    EdtQuery: TEdit;
    BtnPrepareSearch: TButton;
    BtnCancel: TButton;
    LblStatus: TLabel;
    procedure BtnPrepareSearchClick(Sender: TObject);
    procedure BtnCancelClick(Sender: TObject);
  private
    FSearchQuery: string;
    FSearchHistoryId: Integer;
  public
    property SearchQuery: string read FSearchQuery;
    property SearchHistoryId: Integer read FSearchHistoryId;
  end;

var
  FrmSearch: TFrmSearch;

implementation

{$R *.dfm}

uses
  USearchService,
  UJwtTokenStore;

procedure TFrmSearch.BtnCancelClick(Sender: TObject);
begin
  ModalResult := mrCancel;
end;

procedure TFrmSearch.BtnPrepareSearchClick(Sender: TObject);
var
  LSearchService: TSearchService;
  LResult: TSearchCreateResult;
  LScanResult: TScanStartResult;
begin
  FSearchQuery := Trim(EdtQuery.Text);
  if FSearchQuery = '' then
    raise Exception.Create('Arama metni bos olamaz.');

  LblStatus.Caption := 'Search endpoint cagriliyor...';
  LSearchService := TSearchService.Create;
  try
    LResult := LSearchService.CreateSearch(FSearchQuery, TJwtTokenStore.GetToken);
    FSearchHistoryId := LResult.SearchHistoryId;

    LblStatus.Caption := 'Scan baslatiliyor...';
    LScanResult := LSearchService.StartScan(FSearchQuery, FSearchHistoryId, TJwtTokenStore.GetToken);
    if LScanResult.Message <> '' then
      LblStatus.Caption := 'Scan baslatildi. ID: ' + IntToStr(FSearchHistoryId) + ' | ' + LScanResult.Message
    else
      LblStatus.Caption := 'Scan baslatildi. ID: ' + IntToStr(FSearchHistoryId);
  finally
    LSearchService.Free;
  end;

  ModalResult := mrOk;
end;

end.
