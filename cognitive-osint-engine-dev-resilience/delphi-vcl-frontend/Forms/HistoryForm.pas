unit HistoryForm;

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
  TFrmHistory = class(TForm)
    LblTitle: TLabel;
    BtnLoad: TButton;
    BtnClose: TButton;
    MemoHistory: TMemo;
    LblStatus: TLabel;
    procedure BtnLoadClick(Sender: TObject);
    procedure BtnCloseClick(Sender: TObject);
  private
    procedure RenderHistory(const ALines: TStrings);
  public
    { Public declarations }
  end;

var
  FrmHistory: TFrmHistory;

implementation

{$R *.dfm}

uses
  UHistoryService,
  UJwtTokenStore;

procedure TFrmHistory.BtnCloseClick(Sender: TObject);
begin
  Close;
end;

procedure TFrmHistory.BtnLoadClick(Sender: TObject);
var
  LService: THistoryService;
  LData: TSearchHistoryItems;
  I: Integer;
  LLines: TStringList;
begin
  LblStatus.Caption := 'History endpoint cagriliyor...';

  LService := THistoryService.Create;
  LLines := TStringList.Create;
  try
    LData := LService.GetHistory(TJwtTokenStore.GetToken);

    if Length(LData) = 0 then
      LLines.Add('Search history kaydi bulunamadi.')
    else
    begin
      for I := 0 to High(LData) do
      begin
        LLines.Add('ID: ' + IntToStr(LData[I].Id));
        LLines.Add('Query: ' + LData[I].Query);
        LLines.Add('Created At: ' + LData[I].CreatedAt);
        LLines.Add('----------------------------------------');
      end;
    end;

    RenderHistory(LLines);
    LblStatus.Caption := 'Toplam history kaydi: ' + IntToStr(Length(LData));
  finally
    LLines.Free;
    LService.Free;
  end;
end;

procedure TFrmHistory.RenderHistory(const ALines: TStrings);
begin
  MemoHistory.Lines.BeginUpdate;
  try
    MemoHistory.Lines.Assign(ALines);
  finally
    MemoHistory.Lines.EndUpdate;
  end;
end;

end.
