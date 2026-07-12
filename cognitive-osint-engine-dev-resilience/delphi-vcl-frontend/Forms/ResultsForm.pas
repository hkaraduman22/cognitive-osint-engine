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
  Vcl.StdCtrls;

type
  TFrmResults = class(TForm)
    LblTitle: TLabel;
    LblAramaId: TLabel;
    EdtAramaId: TEdit;
    BtnLoad: TButton;
    BtnClose: TButton;
    MemoResults: TMemo;
    LblStatus: TLabel;
    procedure BtnLoadClick(Sender: TObject);
    procedure BtnCloseClick(Sender: TObject);
  private
    procedure RenderResults(const AResultsText: TStrings);
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
  J: Integer;
  LLines: TStringList;
begin
  LAramaId := StrToIntDef(Trim(EdtAramaId.Text), -1);
  if LAramaId <= 0 then
    raise Exception.Create('Gecerli bir arama_id giriniz.');

  LblStatus.Caption := 'Results endpoint cagriliyor...';

  LService := TResultsService.Create;
  LLines := TStringList.Create;
  try
    LData := LService.GetCompanies(LAramaId, TJwtTokenStore.GetToken);

    if Length(LData) = 0 then
      LLines.Add('Kayit bulunamadi.')
    else
    begin
      for I := 0 to High(LData) do
      begin
        LLines.Add('ID: ' + IntToStr(LData[I].Id));
        LLines.Add('Name: ' + LData[I].Name);
        LLines.Add('Industry: ' + LData[I].Industry);
        LLines.Add('City: ' + LData[I].City);
        LLines.Add('Address: ' + LData[I].Address);
        LLines.Add('Website: ' + LData[I].Website);
        LLines.Add('Phone: ' + LData[I].Phone);
        LLines.Add('Email: ' + LData[I].Email);
        LLines.Add('Source URL: ' + LData[I].SourceUrl);
        LLines.Add('Confidence: ' + IntToStr(LData[I].ConfidenceScore));
        LLines.Add('Created At: ' + LData[I].CreatedAt);
        LLines.Add('Updated At: ' + LData[I].UpdatedAt);
        if Length(LData[I].Officials) = 0 then
          LLines.Add('Officials: -')
        else
        begin
          LLines.Add('Officials:');
          for J := 0 to High(LData[I].Officials) do
            LLines.Add('  - ' + LData[I].Officials[J].FullName + ' (' + LData[I].Officials[J].Title + ')');
        end;
        LLines.Add('----------------------------------------');
      end;
    end;

    RenderResults(LLines);
    LblStatus.Caption := 'Toplam kayit: ' + IntToStr(Length(LData));
  finally
    LLines.Free;
    LService.Free;
  end;
end;

procedure TFrmResults.RenderResults(const AResultsText: TStrings);
begin
  MemoResults.Lines.BeginUpdate;
  try
    MemoResults.Lines.Assign(AResultsText);
  finally
    MemoResults.Lines.EndUpdate;
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
